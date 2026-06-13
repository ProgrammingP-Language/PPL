"""
Code generator for TyC.
"""

from typing import Any

from ..utils.nodes import *
from ..utils.visitor import BaseVisitor
from .emitter import *
from .frame import *
from .io import IO_SYMBOL_LIST
from .utils import *



class StringArrayType:
    """Marker type for JVM main(String[] args)."""
    pass


class AutoType(Type):
    def accept(self, visitor, o=None):
        return visitor.visit_auto_type(self, o)


class CodeGenerator(BaseVisitor):
    """Full AST -> Jasmin code generator supporting all TyC features."""

    def __init__(self):
        self.emit = None
        self.functions = {}
        self.structs = {}          # struct_name -> StructDecl node
        self.current_return_type = VoidType()
        self.class_name = "TyC"
        self.switch_stack = []  # brea_label stack riêng cho switch

    # helpers
    
    def _lookup_symbol(self, name: str, sym_list: list) -> Symbol:
        for sym in reversed(sym_list):
            if sym.name == name:
                return sym
        raise RuntimeError(f"Undeclared symbol: {name}")

    def _infer_type(self, node: Expr, o: Access):
        if isinstance(node, IntLiteral):
            return IntType()
        if isinstance(node, FloatLiteral):
            return FloatType()
        if isinstance(node, StringLiteral):
            return StringType()
        if isinstance(node, Identifier):
            sym_type = self._lookup_symbol(node.name, o.sym).type
            if isinstance(sym_type, AutoType):
                return IntType()
            return sym_type
        
        if isinstance(node, AssignExpr):
            return self._infer_type(node.rhs, o)
        
        if isinstance(node, FuncCall):
            ret = self.functions[node.name].type.return_type
            if isinstance(ret, AutoType):
                return IntType()
            return ret
        
        if isinstance(node, BinaryOp):
            if node.operator in ["+", "-", "*", "/", "%"]:
                left_type = self._infer_type(node.left, o)
                right_type = self._infer_type(node.right, o)
                if is_float_type(left_type) or is_float_type(right_type):
                    return FloatType()
                return IntType()
            if node.operator in ["<", "<=", ">", ">=", "==", "!=", "&&", "||"]:
                return IntType()
            
        if isinstance(node, PrefixOp):
            if node.operator == "!":
                return IntType()
            return self._infer_type(node.operand, o)
        
        if isinstance(node, PostfixOp):
            return self._infer_type(node.operand, o)
        
        if isinstance(node, MemberAccess):
            obj_type = self._infer_type(node.obj, o)
            if is_struct_type(obj_type):
                struct_decl = self.structs.get(obj_type.struct_name)
                if struct_decl:
                    for m in struct_decl.members:
                        if m.name == node.member:
                            return m.member_type
            
        if isinstance(node, StructLiteral):
            return None

        return IntType()

    def trans_to_float(self, code: str, src_type, frame) -> str:  # ép kiểu int to float 
        if is_int_type(src_type):
            return code + self.emit.emit_i2f(frame)
        return code

    # Program / Function
   
    def visit_program(self, node: Program, o: Any = None):
        self.emit = Emitter(f"{self.class_name}.j")
        self.emit.print_out(self.emit.emit_prolog(self.class_name))

        for io_sym in IO_SYMBOL_LIST:
            self.functions[io_sym.name] = io_sym

        for decl in node.decls: 
            if isinstance(decl, StructDecl):
                self.structs[decl.name] = decl

        for decl in node.decls:
            if isinstance(decl, FuncDecl):
                return_type = decl.return_type
                if return_type is None or isinstance(return_type, AutoType):
                    return_type = IntType()
                param_types = [
                    IntType() if (p.param_type is None or isinstance(p.param_type, AutoType))
                    else p.param_type
                    for p in decl.params
                ]
                self.functions[decl.name] = Symbol(
                    decl.name, FunctionType(param_types, return_type), CName(self.class_name)
                )

        # Emit struct class files
        for decl in node.decls:
            if isinstance(decl, StructDecl):
                self.emit.emit_struct_class(decl)

        for decl in node.decls:
            if isinstance(decl, FuncDecl):
                self.visit(decl, None)

        self.emit.emit_epilog()


    def visit_func_decl(self, node: FuncDecl, o: Any = None):
        ret_type = node.return_type
        if ret_type is None or isinstance(ret_type, AutoType):
            ret_type = IntType()
        self.current_return_type = ret_type
        frame = Frame(node.name, self.current_return_type)
        frame.enter_scope(True)

        if node.name == "main":
            mtype = FunctionType([StringArrayType()], VoidType())
        else:
            mtype = FunctionType([p.param_type for p in node.params], self.current_return_type)

        self.emit.print_out(self.emit.emit_method(node.name, mtype, True))
        start_label = frame.get_start_label()
        end_label = frame.get_end_label()
        self.emit.print_out(self.emit.emit_label(start_label, frame))

        local_syms: list[Symbol] = []
        if node.name == "main":
            args_idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(
                    args_idx, "args", StringArrayType(), start_label, end_label
                )
            )

        for param in node.params:
            idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(idx, param.name, param.param_type, start_label, end_label)
            )
            local_syms.append(Symbol(param.name, param.param_type, Index(idx)))

        sub_body = SubBody(frame, local_syms)
        self.visit(node.body, sub_body)

        if is_void_type(self.current_return_type):
            self.emit.print_out(self.emit.emit_return(VoidType(), frame))

        self.emit.print_out(self.emit.emit_label(end_label, frame))
        frame.exit_scope()
        self.emit.print_out(self.emit.emit_end_method(frame))


    # Statements
    def visit_block_stmt(self, node: BlockStmt, o: SubBody = None):
        frame = o.frame
        frame.enter_scope(False)
        block_start = frame.get_start_label()
        block_end = frame.get_end_label()
        self.emit.print_out(self.emit.emit_label(block_start, frame))

        save_sym_len = len(o.sym)
        for stmt in node.statements:
            o = self.visit(stmt, o)

        self.emit.print_out(self.emit.emit_label(block_end, frame))
        frame.exit_scope()
        del o.sym[save_sym_len:]
        return o

    def visit_var_decl(self, node: VarDecl, o: SubBody = None):
        frame = o.frame
        idx = frame.get_new_index()

        var_type = node.var_type
        is_auto = (var_type is None or isinstance(var_type, AutoType))
        if is_auto:
            if node.init_value is not None:
                if isinstance(node.init_value, StructLiteral):
                    var_type = IntType()
                else:
                    inferred = self._infer_type(node.init_value, Access(frame, o.sym))
                    if inferred is None or isinstance(inferred, AutoType):
                        var_type = IntType()
                    else:
                        var_type = inferred
            else:
                var_type = IntType()  

        self.emit.print_out(
            self.emit.emit_var(
                idx, node.name, var_type, frame.get_start_label(), frame.get_end_label()
            )
        )

        if node.init_value is not None:
            if isinstance(node.init_value, StructLiteral) and is_struct_type(var_type):
                rhs_code, rhs_type = self.emit_struct_literal(
                    node.init_value, Access(frame, o.sym), var_type.struct_name
                )
            else:
                rhs_code, rhs_type = self.visit(node.init_value, Access(frame, o.sym))
            if is_auto and is_struct_type(rhs_type) and not is_struct_type(var_type):
                var_type = rhs_type
            if is_float_type(var_type) and is_int_type(rhs_type):
                rhs_code = self.trans_to_float(rhs_code, rhs_type, frame)
            # Deep copy struct 
            if is_struct_type(rhs_type) and not isinstance(node.init_value, StructLiteral):
                rhs_code = self.emit_struct_deep_copy(rhs_code, rhs_type.struct_name, Access(frame, o.sym))
            self.emit.print_out(rhs_code)
            self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
        else:
            if is_int_type(var_type):
                self.emit.print_out(self.emit.emit_push_iconst(0, frame))
                self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
            elif is_float_type(var_type):
                self.emit.print_out(self.emit.emit_push_fconst("0.0", frame))
                self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
            elif is_string_type(var_type):
                self.emit.print_out(self.emit.emit_push_const("", StringType(), frame))
                self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
            elif is_struct_type(var_type):
                struct_name = var_type.struct_name
                self.emit.print_out(self.emit.emit_new_instance(struct_name, frame))
                self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))

        o.sym.append(Symbol(node.name, var_type, Index(idx)))
        return o

    def visit_expr_stmt(self, node: ExprStmt, o: SubBody = None):
        code, expr_type = self.visit(node.expr, Access(o.frame, o.sym))
        self.emit.print_out(code)
        if not is_void_type(expr_type):
            self.emit.print_out(self.emit.emit_pop(o.frame))
        return o

    def stmt_terminate(self, node) -> bool:
        if isinstance(node, ReturnStmt):
            return True
        if isinstance(node, BreakStmt):
            return True
        if isinstance(node, ContinueStmt):
            return True
        if isinstance(node, BlockStmt):
            for s in node.statements:
                if self.stmt_terminate(s):
                    return True
            return False
        if isinstance(node, IfStmt):
            if node.else_stmt is None:
                return False
            return self.stmt_terminate(node.then_stmt) and self.stmt_terminate(node.else_stmt)
        return False

    def visit_if_stmt(self, node: IfStmt, o: SubBody = None):
        frame = o.frame
        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        else_label = frame.get_new_label()
        end_label = frame.get_new_label()
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(else_label, frame))
        self.visit(node.then_stmt, o) # chay qua nhanh then ko can chay vao else  
        then_terminate = self.stmt_terminate(node.then_stmt)
        if not then_terminate:
            self.emit.print_out(self.emit.emit_goto(end_label, frame))
        self.emit.print_out(self.emit.emit_label(else_label, frame))
        if node.else_stmt:
            self.visit(node.else_stmt, o)
        self.emit.print_out(self.emit.emit_label(end_label, frame))
        return o

    def visit_while_stmt(self, node: WhileStmt, o: SubBody = None):
        frame = o.frame
        loop_start = frame.get_new_label()
        frame.enter_loop()
        con_label = frame.get_continue_label()
        brea_label = frame.get_break_label()

        self.emit.print_out(self.emit.emit_label(loop_start, frame))
        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(brea_label, frame))
        self.visit(node.body, o)
        self.emit.print_out(self.emit.emit_label(con_label, frame))
        self.emit.print_out(self.emit.emit_goto(loop_start, frame))
        self.emit.print_out(self.emit.emit_label(brea_label, frame))
        frame.exit_loop()
        return o

    def visit_for_stmt(self, node: ForStmt, o: SubBody = None):
        frame = o.frame
        frame.enter_scope(False)
        for_start = frame.get_start_label()
        for_end = frame.get_end_label()
        self.emit.print_out(self.emit.emit_label(for_start, frame))

        if node.init is not None:
            o = self.visit(node.init, o)

        loop_start = frame.get_new_label()

        frame.enter_loop()
        con_label = frame.get_continue_label()
        brea_label = frame.get_break_label()

        self.emit.print_out(self.emit.emit_label(loop_start, frame))

        # condition
        if node.condition is not None:
            cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
            self.emit.print_out(cond_code)
            self.emit.print_out(self.emit.emit_if_false(brea_label, frame))

        # body
        self.visit(node.body, o)

        # continue label - update
        self.emit.print_out(self.emit.emit_label(con_label, frame))
        if node.update is not None:
            upd_code, upd_type = self.visit(node.update, Access(frame, o.sym))
            self.emit.print_out(upd_code)
            if not is_void_type(upd_type):
                self.emit.print_out(self.emit.emit_pop(frame))

        self.emit.print_out(self.emit.emit_goto(loop_start, frame))
        self.emit.print_out(self.emit.emit_label(brea_label, frame))
        frame.exit_loop()

        self.emit.print_out(self.emit.emit_label(for_end, frame))
        frame.exit_scope()
        return o

    def visit_switch_stmt(self, node: SwitchStmt, o: SubBody = None):
        frame = o.frame

        case_labels = [frame.get_new_label() for _ in node.cases]
        default_label = frame.get_new_label()
        brea_label = frame.get_new_label()
        self.switch_stack.append(brea_label)

        # Emit 
        for i, case in enumerate(node.cases):
            expr_code, _ = self.visit(node.expr, Access(frame, o.sym))
            val_code, _ = self.visit(case.expr, Access(frame, o.sym))
            self.emit.print_out(expr_code)
            self.emit.print_out(val_code)
            eq_code = self.emit.jvm.emitIFICMPEQ(case_labels[i])
            frame.pop(); frame.pop()
            self.emit.print_out(eq_code)

        if node.default_case is not None:
            self.emit.print_out(self.emit.emit_goto(default_label, frame))
        else:
            self.emit.print_out(self.emit.emit_goto(brea_label, frame))

        saved_index = frame.get_curr_index()
        switch_sym = list(o.sym)

        for i, case in enumerate(node.cases):
            self.emit.print_out(self.emit.emit_label(case_labels[i], frame))
            inner_o = SubBody(frame, list(switch_sym))
            for stmt in case.statements:
                inner_o = self.visit(stmt, inner_o)
            switch_sym = inner_o.sym  

        if node.default_case is not None:
            self.emit.print_out(self.emit.emit_label(default_label, frame))
            inner_o = SubBody(frame, list(switch_sym))
            for stmt in node.default_case.statements:
                inner_o = self.visit(stmt, inner_o)

        self.emit.print_out(self.emit.emit_label(brea_label, frame))
        self.switch_stack.pop()
        frame.set_curr_index(saved_index)
        return o

    def visit_case_stmt(self, node: CaseStmt, o: Any = None):
        return o

    def visit_default_stmt(self, node: DefaultStmt, o: Any = None):
        return o

    def visit_return_stmt(self, node: ReturnStmt, o: SubBody = None):
        if node.expr is None:
            self.emit.print_out(self.emit.emit_return(VoidType(), o.frame))
            return o
        code, ret_type = self.visit(node.expr, Access(o.frame, o.sym))
        if is_float_type(self.current_return_type) and is_int_type(ret_type):
            code = self.trans_to_float(code, ret_type, o.frame)
            ret_type = FloatType()
        self.emit.print_out(code)
        self.emit.print_out(self.emit.emit_return(ret_type, o.frame))
        return o

    def visit_break_stmt(self, node: BreakStmt, o: SubBody = None):
        frame = o.frame
        if self.switch_stack:
            brea_label = self.switch_stack[-1]
        else:
            brea_label = frame.get_break_label()
        self.emit.print_out(self.emit.emit_goto(brea_label, frame))
        return o

    def visit_continue_stmt(self, node: ContinueStmt, o: SubBody = None):
        frame = o.frame
        con_label = frame.get_continue_label()
        self.emit.print_out(self.emit.emit_goto(con_label, frame))
        return o

    def visit_binary_op(self, node: BinaryOp, o: Access = None):
        left_code, left_type = self.visit(node.left, o)
        right_code, right_type = self.visit(node.right, o)
        frame = o.frame

        if node.operator == "&&":
            return self.emit_and(node, o)
        if node.operator == "||":
            return self.emit_or(node, o)

        if node.operator in ["+", "-", "*", "/"]:
            if is_float_type(left_type) or is_float_type(right_type):
                result_type = FloatType()
                if is_int_type(left_type):
                    left_code = self.trans_to_float(left_code, left_type, frame)
                if is_int_type(right_type):
                    right_code = self.trans_to_float(right_code, right_type, frame)
            else:
                result_type = IntType()

            if node.operator in ["+", "-"]:
                op_code = self.emit.emit_add_op(node.operator, result_type, frame)
            else:
                op_code = self.emit.emit_mul_op(node.operator, result_type, frame)
            return left_code + right_code + op_code, result_type

        if node.operator == "%":
            return left_code + right_code + self.emit.emit_mod(frame), IntType()

        if node.operator in ["<", "<=", ">", ">=", "==", "!="]:
            op_type = FloatType() if is_float_type(left_type) or is_float_type(right_type) else IntType()
            if is_float_type(op_type):
                if is_int_type(left_type):
                    left_code = self.trans_to_float(left_code, left_type, frame)
                if is_int_type(right_type):
                    right_code = self.trans_to_float(right_code, right_type, frame)
            return (
                left_code + right_code + self.emit.emit_re_op(node.operator, op_type, frame),
                IntType(),
            )

        raise RuntimeError(f"Unsupported binary operator: {node.operator}")

    def emit_and(self, node: BinaryOp, o: Access):
        frame = o.frame
        left_code, left_type = self.visit(node.left, o)
        right_code, right_type = self.visit(node.right, o)
        false_label = frame.get_new_label()
        end_label = frame.get_new_label()

        code = left_code
        code += self.emit.emit_if_false(false_label, frame)
        code += right_code
        code += self.emit.emit_if_false(false_label, frame)
        code += self.emit.emit_push_iconst(1, frame)
        code += self.emit.emit_goto(end_label, frame)
        code += self.emit.emit_label(false_label, frame)
        code += self.emit.emit_push_iconst(0, frame)
        code += self.emit.emit_label(end_label, frame)
        return code, IntType()

    def emit_or(self, node: BinaryOp, o: Access):
        """Short-circuit OR: result is 1 if either non-zero, else 0."""
        frame = o.frame
        left_code, left_type = self.visit(node.left, o)
        right_code, right_type = self.visit(node.right, o)
        true_label = frame.get_new_label()
        end_label = frame.get_new_label()

        code = left_code
        code += self.emit.emit_if_true(true_label, frame)
        code += right_code
        code += self.emit.emit_if_true(true_label, frame)
        code += self.emit.emit_push_iconst(0, frame)
        code += self.emit.emit_goto(end_label, frame)
        code += self.emit.emit_label(true_label, frame)
        code += self.emit.emit_push_iconst(1, frame)
        code += self.emit.emit_label(end_label, frame)
        return code, IntType()

    def visit_prefix_op(self, node: PrefixOp, o: Access = None):
        frame = o.frame
        op = node.operator

        if op == "!":
            operand_code, operand_type = self.visit(node.operand, o)
            true_label = frame.get_new_label()
            end_label = frame.get_new_label()
            code = operand_code
            code += self.emit.emit_if_false(true_label, frame)
            code += self.emit.emit_push_iconst(0, frame)
            code += self.emit.emit_goto(end_label, frame)
            code += self.emit.emit_label(true_label, frame)
            code += self.emit.emit_push_iconst(1, frame)
            code += self.emit.emit_label(end_label, frame)
            return code, IntType()

        if op == "+":
            return self.visit(node.operand, o)

        if op == "-":
            operand_code, operand_type = self.visit(node.operand, o)
            return operand_code + self.emit.emit_neg_op(operand_type, frame), operand_type

        if op in ["++", "--"]:
            if not isinstance(node.operand, Identifier):
                raise RuntimeError("++ / -- only supported on identifiers")
            sym = self._lookup_symbol(node.operand.name, o.sym)
            idx = sym.value.value
            var_type = sym.type
            load_code = self.emit.emit_read_var(node.operand.name, var_type, idx, frame)
            one_code = self.emit.emit_push_iconst(1, frame)
            if op == "++":
                arith = self.emit.emit_add_op("+", var_type, frame)
            else:
                arith = self.emit.emit_add_op("-", var_type, frame)
            dup_code = self.emit.emit_dup(frame)
            store_code = self.emit.emit_write_var(node.operand.name, var_type, idx, frame)
            return load_code + one_code + arith + dup_code + store_code, var_type

        raise RuntimeError(f"Unsupported prefix op: {op}")

    def visit_postfix_op(self, node: PostfixOp, o: Access = None):
        frame = o.frame
        op = node.operator

        if op in ["++", "--"]:
            if not isinstance(node.operand, Identifier):
                raise RuntimeError("++ / -- only supported on identifiers")
            sym = self._lookup_symbol(node.operand.name, o.sym)
            idx = sym.value.value
            var_type = sym.type
            load_code = self.emit.emit_read_var(node.operand.name, var_type, idx, frame)
            dup_code = self.emit.emit_dup(frame)
            one_code = self.emit.emit_push_iconst(1, frame)
            if op == "++":
                arith = self.emit.emit_add_op("+", var_type, frame)
            else:
                arith = self.emit.emit_add_op("-", var_type, frame)
            store_code = self.emit.emit_write_var(node.operand.name, var_type, idx, frame)
            return load_code + dup_code + one_code + arith + store_code, var_type

        raise RuntimeError(f"Unsupported postfix op: {op}")

    def visit_assign_expr(self, node: AssignExpr, o: Access = None):
        frame = o.frame

        if isinstance(node.lhs, Identifier):
            lhs_sym = self._lookup_symbol(node.lhs.name, o.sym)
            idx = lhs_sym.value.value
            lhs_type = lhs_sym.type

            # Auto type
            if isinstance(lhs_type, AutoType):
                if isinstance(node.rhs, StructLiteral):
                    rhs_code, rhs_type = self.visit(node.rhs, o)
                    lhs_sym.type = rhs_type
                    lhs_type = rhs_type
                else:
                    # Infer type từ RHS expression
                    inferred = self._infer_type(node.rhs, o)
                    if inferred is None or isinstance(inferred, AutoType):
                        inferred = IntType()
                    lhs_sym.type = inferred
                    lhs_type = inferred
                    rhs_code, rhs_type = self.visit(node.rhs, o)
            elif isinstance(node.rhs, StructLiteral) and is_struct_type(lhs_type):
                rhs_code, rhs_type = self.emit_struct_literal(
                    node.rhs, o, lhs_type.struct_name
                )
            else:
                rhs_code, rhs_type = self.visit(node.rhs, o)

            if is_int_type(lhs_type) and is_float_type(rhs_type):
                lhs_sym.type = FloatType()
                lhs_type = FloatType()
            
            if is_float_type(lhs_type) and is_int_type(rhs_type):
                rhs_code = self.trans_to_float(rhs_code, rhs_type, frame)
                rhs_type = FloatType()

            # Deep copy struct if rhs is not a StructLiteral 
            if is_struct_type(lhs_type) and not isinstance(node.rhs, StructLiteral):
                rhs_code = self.emit_struct_deep_copy(rhs_code, lhs_type.struct_name, o)

            dup_code = self.emit.emit_dup(frame)
            store_code = self.emit.emit_write_var(node.lhs.name, lhs_type, idx, frame)
            return rhs_code + dup_code + store_code, lhs_type

        if isinstance(node.lhs, MemberAccess):
            return self.emit_member_assign(node, o)

        raise RuntimeError("Unsupported LHS in assignment")

    def emit_member_assign(self, node: AssignExpr, o: Access):
       
        frame = o.frame
        ma = node.lhs
        obj_code, obj_type = self.visit(ma.obj, o)
        struct_decl = self.structs.get(obj_type.struct_name)
        field_type = None
        for m in struct_decl.members:
            if m.name == ma.member:
                field_type = m.member_type
                break
        rhs_code, rhs_type = self.visit(node.rhs, o)
        if is_float_type(field_type) and is_int_type(rhs_type):
            rhs_code = self.trans_to_float(rhs_code, rhs_type, frame)
        dup_code = self.emit.emit_dup_x1(frame)
        put_code = self.emit.emit_put_field(f"{obj_type.struct_name}/{ma.member}", field_type, frame)
        return obj_code + rhs_code + dup_code + put_code, field_type

    def visit_func_call(self, node: FuncCall, o: Access = None):
        frame = o.frame
        fn_sym = self.functions[node.name]
        fn_type = fn_sym.type
        code = ""
        for i, arg in enumerate(node.args):
            arg_code, arg_type = self.visit(arg, o)
            if i < len(fn_type.param_types) and is_float_type(fn_type.param_types[i]) and is_int_type(arg_type):
                arg_code = self.trans_to_float(arg_code, arg_type, frame)
            # Deep copy struct arguments 
            elif is_struct_type(arg_type):
                arg_code = self.emit_struct_deep_copy(arg_code, arg_type.struct_name, o)
            code += arg_code
        code += self.emit.emit_invoke_static(f"{fn_sym.value.value}/{node.name}", fn_type, frame)
        return code, fn_type.return_type

    def visit_identifier(self, node: Identifier, o: Access = None):
        sym = self._lookup_symbol(node.name, o.sym)
        sym_type = sym.type
        if isinstance(sym_type, AutoType):
            sym_type = IntType()
            sym.type = sym_type
        return self.emit.emit_read_var(node.name, sym_type, sym.value.value, o.frame), sym_type

    def visit_int_literal(self, node: IntLiteral, o: Access = None):
        return self.emit.emit_push_iconst(node.value, o.frame), IntType()

    def visit_float_literal(self, node: FloatLiteral, o: Access = None):
        return self.emit.emit_push_fconst(str(node.value), o.frame), FloatType()

    def visit_string_literal(self, node: StringLiteral, o: Access = None):
        return self.emit.emit_push_const(node.value, StringType(), o.frame), StringType()

    def visit_member_access(self, node: MemberAccess, o: Access = None):
        frame = o.frame
        obj_code, obj_type = self.visit(node.obj, o)
        struct_decl = self.structs.get(obj_type.struct_name)
        field_type = None
        for m in struct_decl.members:
            if m.name == node.member:
                field_type = m.member_type
                break
        get_code = self.emit.emit_get_field(f"{obj_type.struct_name}/{node.member}", field_type, frame)
        return obj_code + get_code, field_type

    def emit_struct_deep_copy(self, src_code: str, struct_name: str, o: Access) -> str:
        
        frame = o.frame
        struct_decl = self.structs[struct_name]
        src_idx = frame.get_new_index()
        dst_idx = frame.get_new_index()

        code = src_code
        frame.pop()
        code += self.emit.jvm.emitASTORE(src_idx)
        frame.push()
        code += self.emit.jvm.emitNEW(struct_name)
        frame.push()
        code += self.emit.jvm.emitDUP()
        frame.pop()
        code += self.emit.jvm.emitINVOKESPECIAL(struct_name + "/<init>", "()V")
        frame.pop()
        code += self.emit.jvm.emitASTORE(dst_idx)

        for m in struct_decl.members:
            field_type = m.member_type
            jvm_ftype = self.emit.get_jvm_type(field_type)
            if is_struct_type(field_type):
                raw_src_code = (
                    self.emit.jvm.emitALOAD(src_idx) +
                    self.emit.jvm.emitGETFIELD(f"{struct_name}/{m.name}", jvm_ftype))
                
                frame.push()          
                frame.pop()           
                frame.push()          
                nested_code = self.emit_struct_deep_copy(raw_src_code, field_type.struct_name, o)
                val_idx = frame.get_new_index()
                frame.pop()
                code += nested_code + self.emit.jvm.emitASTORE(val_idx)
                frame.push()
                code += self.emit.jvm.emitALOAD(dst_idx)
                frame.push()
                code += self.emit.jvm.emitALOAD(val_idx)
                frame.pop(); frame.pop()
                code += self.emit.jvm.emitPUTFIELD(f"{struct_name}/{m.name}", jvm_ftype)

            else:
                frame.push()
                code += self.emit.jvm.emitALOAD(dst_idx)
                frame.push()
                code += self.emit.jvm.emitALOAD(src_idx)
                frame.pop(); frame.push()   
                code += self.emit.jvm.emitGETFIELD(f"{struct_name}/{m.name}", jvm_ftype)
                frame.pop(); frame.pop()  
                code += self.emit.jvm.emitPUTFIELD(f"{struct_name}/{m.name}", jvm_ftype)
                
        frame.push()
        code += self.emit.jvm.emitALOAD(dst_idx)
        return code

    def emit_struct_literal(self, node: StructLiteral, o: Access, struct_name: str):
        frame = o.frame
        struct_decl = self.structs[struct_name]
        struct_type = CodeGenStructType(struct_name)

        tmp_idx = frame.get_new_index()
        code = self.emit.emit_new_instance(struct_name, frame)
        code += self.emit.emit_write_var("__struct_tmp__", struct_type, tmp_idx, frame)

        for member, val_expr in zip(struct_decl.members, node.values):
            field_type = member.member_type
            val_code, val_type = self.visit(val_expr, o)
            if is_float_type(field_type) and is_int_type(val_type):
                val_code = self.trans_to_float(val_code, val_type, frame)
            load_code = self.emit.emit_read_var("__struct_tmp__", struct_type, tmp_idx, frame)
            put_code = self.emit.emit_put_field(f"{struct_name}/{member.name}", field_type, frame)
            code += load_code + val_code + put_code

        code += self.emit.emit_read_var("__struct_tmp__", struct_type, tmp_idx, frame)
        return code, struct_type


# Visitor method 

    def visit_struct_literal(self, node: StructLiteral, o: Access = None):
        raise RuntimeError()    
        
    def visit_struct_decl(self, node: StructDecl, o: Any = None):
        return None

    def visit_member_decl(self, node: MemberDecl, o: Any = None):
        return None

    def visit_param(self, node: Param, o: Any = None):
        return None

    def visit_int_type(self, node: IntType, o: Any = None):
        return node

    def visit_float_type(self, node: FloatType, o: Any = None):
        return node

    def visit_string_type(self, node: StringType, o: Any = None):
        return node

    def visit_void_type(self, node: VoidType, o: Any = None):
        return node

    def visit_struct_type(self, node, o: Any = None):
        return node

    def visit_auto_type(self, node, o: Any = None):
        return node