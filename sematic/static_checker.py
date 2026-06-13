"""
Static Semantic Checker for TyC Programming Language

This module implements a comprehensive static semantic checker using visitor pattern
for the TyC procedural programming language. It performs type checking,
scope management, type inference, and detects all semantic errors as
specified in the TyC language specification.
"""

from functools import reduce
from typing import (
    Dict,
    List,
    Set,
    Optional,
    Any,
    Tuple,
    NamedTuple,
    Union,
    TYPE_CHECKING,
)
from ..utils.visitor import ASTVisitor
from ..utils.nodes import (
    ASTNode,
    Program,
    StructDecl,
    MemberDecl,
    FuncDecl,
    Param,
    VarDecl,
    IfStmt,
    WhileStmt,
    ForStmt,
    BreakStmt,
    ContinueStmt,
    ReturnStmt,
    BlockStmt,
    SwitchStmt,
    CaseStmt,
    DefaultStmt,
    Type,
    IntType,
    FloatType,
    StringType,
    VoidType,
    StructType,
    BinaryOp,
    PrefixOp,
    PostfixOp,
    AssignExpr,
    MemberAccess,
    FuncCall,
    Identifier,
    StructLiteral,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    ExprStmt,
    Expr,
    Stmt,
    Decl,
)

# Type aliases for better type hints
TyCType = Union[IntType, FloatType, StringType, VoidType, StructType]
from .static_error import (
    StaticError,
    Redeclared,
    UndeclaredIdentifier,
    UndeclaredFunction,
    UndeclaredStruct,
    TypeCannotBeInferred,
    TypeMismatchInStatement,
    TypeMismatchInExpression,
    MustInLoop,
)
# ---------------------------------------------------------------------------
# AUTO 
# ---------------------------------------------------------------------------


class AutoType:
    def __repr__(self):
        return "auto"

AUTO = AutoType()


# ---------------------------------------------------------------------------
# Các hàm tiện ích kiểm tra kiểu
# ---------------------------------------------------------------------------

def types_equal(x1, x2) -> bool:
    if type(x1) != type(x2):
        return False
    if isinstance(x1, StructType) and isinstance(x2, StructType):
        return x1.struct_name == x2.struct_name
    return True


def _is_assignable(kieu_trai, kieu_phai) -> bool:
    return types_equal(kieu_trai, kieu_phai)


def _is_decl_compatible(kieu_khai_bao, kieu_gia_tri) -> bool:
    return types_equal(kieu_khai_bao, kieu_gia_tri)


# ---------------------------------------------------------------------------
# Scope / Symbol Table
# 
# ---------------------------------------------------------------------------

class Env:

    def __init__(self, cha: Optional["Env"] = None):
        self.bang: Dict[str, Any] = {}   # bảng tên -> kiểu của scope này
        self.parent = cha

    def khai_bao(self, ten: str, kieu) -> bool:
        if ten in self.bang:
            return False
        self.bang[ten] = kieu
        return True

    def tim_kiem(self, ten: str):
        if ten in self.bang:
            return self.bang[ten]
        if self.parent is not None:
            return self.parent.tim_kiem(ten)
        return None

    def declare_local(self, ten: str, kieu) -> bool:
        return self.khai_bao(ten, kieu)

    def lookup(self, ten: str):
        return self.tim_kiem(ten)


# ---------------------------------------------------------------------------
# Các hàm built-in
# ---------------------------------------------------------------------------

HAM_BUILTIN: Dict[str, Tuple] = {
    "readInt":     ([], IntType()),
    "readFloat":   ([], FloatType()),
    "readString":  ([], StringType()),
    "printInt":    ([IntType()], VoidType()),
    "printFloat":  ([FloatType()], VoidType()),
    "printString": ([StringType()], VoidType()),
}


# ---------------------------------------------------------------------------
# Static Semantic Checker chính
# ---------------------------------------------------------------------------

class StaticChecker(ASTVisitor):

    def __init__(self):
        self.bang_struct: Dict[str, List[MemberDecl]] = {}
        self.bang_ham: Dict[str, Tuple] = {}

    def check_program(self, node: " Program "):
        self.visit_program(node, None)

    # =========================================================================
    #  Khai báo toàn cục (struct, hàm)
    # =========================================================================

    def visit_program(self, node: " Program ", o: Any = None):
        bang_struct: Dict = {}
        bang_ham: Dict = {}

        for ten, chu_ky in HAM_BUILTIN.items():
            bang_ham[ten] = chu_ky

        o = {"structs": bang_struct, "funcs": bang_ham}

        # Duyệt từng khai báo
        for khai_bao in node.decls:
            if isinstance(khai_bao, StructDecl):
                self.visit_struct_decl(khai_bao, o)
            elif isinstance(khai_bao, FuncDecl):
                self.visit_func_decl(khai_bao, o)

        self.bang_struct = bang_struct
        self.bang_ham = bang_ham

    def visit_struct_decl(self, node: "StructDecl", o: Any = None):
        bang_struct = o["structs"]

        # Kiểm tra struct trùng tên
        if node.name in bang_struct:
            raise Redeclared("Struct", node.name)

        # Kiểm tra ( check ) các field trong struct
        check : Dict[str, bool] = {}
        for field in node.members:
            self.visit_member_decl(field, o)
            if field.name in check:
                raise Redeclared("Member", field.name)
            check[field.name] = True

        # Đăng ký struct vào bảng
        bang_struct[node.name] = node.members

    def visit_member_decl(self, node: "MemberDecl", o: Any = None):
        self.kiem_tra_kieu(node.member_type, o)

    def visit_func_decl(self, node: "FuncDecl", o: Any = None):
        bang_struct = o["structs"]
        bang_ham = o["funcs"]

        # Bước 1: Kiểm tra tên hàm trùng
        if node.name in bang_ham:
            raise Redeclared("Function", node.name)

        # Bước 2: Xử lý kiểu trả về ( kieu_tra_ve)
        if node.return_type is not None:
            self.kiem_tra_kieu(node.return_type, o)
            kieu_tra_ve = node.return_type
        else:
            kieu_tra_ve = AUTO

        # Bước 3: Duyệt tham số
        danh_sach_kieu_param = []
        ten_param_da_co: Dict[str, bool] = {}

        for param in node.params:
            kieu_p = self.visit_param(param, o)
            if param.name in ten_param_da_co:
                raise Redeclared("Parameter", param.name)
            ten_param_da_co[param.name] = True
            danh_sach_kieu_param.append(kieu_p)

        
        scope_ham = Env()
        for param, kieu_p in zip(node.params, danh_sach_kieu_param):
            scope_ham.khai_bao(param.name, kieu_p)

        # Context khi duyệt body hàm
        ctx_ham = {
            "structs": bang_struct,
            "funcs": bang_ham,
            "env": scope_ham,
            "return_type": kieu_tra_ve,   # kiểu trả về (có thể đang là AUTO)
            "in_loop": False,             
            "in_switch": False,           
            "param_names": set(ten_param_da_co.keys()), 
            "auto_vars": [],              
        }

        
        bang_ham[node.name] = (danh_sach_kieu_param, kieu_tra_ve)

        
        if node.body is not None:
            for stmt in node.body.statements:
                self.duyet_stmt(stmt, ctx_ham)

        
        for (bien_auto, scope_auto) in ctx_ham.get("auto_vars", []):
            if isinstance(scope_auto.lookup(bien_auto.name), AutoType):
                raise TypeCannotBeInferred(node.body)
            # Write-back: ghi kiểu đã resolve ngược vào AST node
            bien_auto.var_type = scope_auto.lookup(bien_auto.name)

        kieu_tra_ve_cuoi = ctx_ham["return_type"]
        if isinstance(kieu_tra_ve_cuoi, AutoType):
            kieu_tra_ve_cuoi = VoidType()
        bang_ham[node.name] = (danh_sach_kieu_param, kieu_tra_ve_cuoi)

    def visit_param(self, node: "Param", o: Any = None):
        """Kiểm tra tham số hàm, trả về kiểu của tham số đó."""
        self.kiem_tra_kieu(node.param_type, o)
        return node.param_type

    # =========================================================================
    #  kiểm tra struct 
    # =========================================================================

    def kiem_tra_kieu(self, kieu, o: Any):
        if isinstance(kieu, StructType):
            bang_struct = o["structs"]
            if kieu.struct_name not in bang_struct:
                raise UndeclaredStruct(kieu.struct_name)

    # =========================================================================
    #  Visitor cho các kiểu dữ liệu 
    # =========================================================================

    def visit_int_type(self, node: "IntType", o: Any = None):
        return node

    def visit_float_type(self, node: "FloatType", o: Any = None):
        return node

    def visit_string_type(self, node: "StringType", o: Any = None):
        return node

    def visit_void_type(self, node: "VoidType", o: Any = None):
        return node

    def visit_struct_type(self, node: "StructType", o: Any = None):
        return node

    # =========================================================================
    # Statements
    # =========================================================================

    def duyet_stmt(self, stmt, o):
        if isinstance(stmt, VarDecl):
            self.visit_var_decl(stmt, o)
        elif isinstance(stmt, IfStmt):
            self.visit_if_stmt(stmt, o)
        elif isinstance(stmt, WhileStmt):
            self.visit_while_stmt(stmt, o)
        elif isinstance(stmt, ForStmt):
            self.visit_for_stmt(stmt, o)
        elif isinstance(stmt, SwitchStmt):
            self.visit_switch_stmt(stmt, o)
        elif isinstance(stmt, BreakStmt):
            self.visit_break_stmt(stmt, o)
        elif isinstance(stmt, ContinueStmt):
            self.visit_continue_stmt(stmt, o)
        elif isinstance(stmt, ReturnStmt):
            self.visit_return_stmt(stmt, o)
        elif isinstance(stmt, BlockStmt):
            self.visit_block_stmt(stmt, o)
        elif isinstance(stmt, ExprStmt):
            self.visit_expr_stmt(stmt, o)

    def visit_block_stmt(self, node: "BlockStmt", o: Any = None):
        # Tạo scope con
        scope_khoi = Env(cha=o["env"])
        auto_vars_khoi = []
        ctx_khoi = dict(o, env=scope_khoi, auto_vars=auto_vars_khoi)

        # Duyệt từng câu lệnh trong khối
        for stmt in node.statements:
            self.duyet_stmt(stmt, ctx_khoi)

        # Sau khi duyệt xong khối, kiểm tra auto vars 
        for (bien_auto, scope_auto) in auto_vars_khoi:
            if isinstance(scope_auto.lookup(bien_auto.name), AutoType):
                raise TypeCannotBeInferred(node)
            # Write-back: ghi kiểu đã resolve ngược vào AST node
            bien_auto.var_type = scope_auto.lookup(bien_auto.name)

        o["return_type"] = ctx_khoi["return_type"]

    def visit_var_decl(self, node: "VarDecl", o: Any = None):
        scope: Env = o["env"]

        # Xác định kiểu khai báo: nếu null thì là auto
        kieu_khai_bao = node.var_type if node.var_type is not None else AUTO

        if node.var_type is not None:
            self.kiem_tra_kieu(node.var_type, o)
        if node.init_value is not None:
            if isinstance(node.init_value, StructLiteral) and not isinstance(kieu_khai_bao, AutoType):
                self.kiem_tra_struct_literal(node.init_value, kieu_khai_bao, node, o)
            else:
                kieu_gia_tri = self.duyet_expr(node.init_value, o)

                if isinstance(kieu_khai_bao, AutoType):
                    if isinstance(kieu_gia_tri, AutoType):
                        # Cả 2 đều auto
                        toan_hang_auto = getattr(node.init_value, "_auto_operands", None)
                        if toan_hang_auto is not None:
                            kieu_da_biet = getattr(node.init_value, "_known_type", None)
                            if isinstance(kieu_da_biet, FloatType):
                                raise TypeCannotBeInferred(node.init_value)
                            known_side_is_typed = False
                            all_auto_identifiers = True  # True nếu tất cả toán hạng đều là auto Identifier (không có IntLiteral)
                            for operand in toan_hang_auto:
                                if isinstance(operand, Identifier):
                                    kieu_op = o["env"].lookup(operand.name)
                                    if kieu_op is not None and not isinstance(kieu_op, AutoType):
                                        known_side_is_typed = True
                                        break
                                elif isinstance(operand, IntLiteral):
                                    # Có IntLiteral -> vẫn có thể defer suy kiểu sau
                                    all_auto_identifiers = False
                                else:
                                    known_side_is_typed = True
                                    break
                            if known_side_is_typed:
                                raise TypeCannotBeInferred(node.init_value)
                            elif all_auto_identifiers:
                                # Tất cả toán hạng đều là auto Identifier, không có IntLiteral -> không suy được
                                raise TypeCannotBeInferred(node.init_value)
                            # else: có IntLiteral -> defer, để cuối block/func check
                        else:
                            kieu_khai_bao = kieu_gia_tri
                    else:
                        kieu_khai_bao = kieu_gia_tri

                elif isinstance(kieu_gia_tri, AutoType):
                    toan_hang_auto = getattr(node.init_value, '_auto_operands', None)
                    if toan_hang_auto is None:
                        # Giá trị đơn giản 
                        if isinstance(node.init_value, Identifier):
                            self.cap_nhat_kieu_auto(node.init_value.name, kieu_khai_bao, o["env"])
                        elif isinstance(node.init_value, FuncCall):
                            raise TypeCannotBeInferred(node.init_value)
                        else:
                            raise TypeMismatchInStatement(node)
                    else:
                        kieu_da_biet = getattr(node.init_value, '_known_type', None)
                        if kieu_da_biet is not None and isinstance(kieu_da_biet, IntType) and isinstance(kieu_khai_bao, IntType):
                            for toan_hang in toan_hang_auto:
                                if isinstance(toan_hang, Identifier):
                                    kieu_th = o["env"].lookup(toan_hang.name)
                                    if isinstance(kieu_th, AutoType):
                                        self.cap_nhat_kieu_auto(toan_hang.name, IntType(), o["env"])
                        else:
                            
                            raise TypeCannotBeInferred(node.init_value)
                else:
                    if not _is_decl_compatible(kieu_khai_bao, kieu_gia_tri):
                        raise TypeMismatchInStatement(node)

        # Kiểm tra redeclared: param cùng tên trong scope hàm
        ten_params = o.get("param_names", set())
        if node.name in ten_params and scope.parent is not None:
            raise Redeclared("Variable", node.name)

        # Đăng ký biến vào scope hiện tại
        if not scope.khai_bao(node.name, kieu_khai_bao):
            raise Redeclared("Variable", node.name)

        if isinstance(kieu_khai_bao, AutoType):
            ds_auto = o.get("auto_vars")
            if ds_auto is not None:
                ds_auto.append((node, scope))
        else:
            # Write-back: ghi kiểu đã suy ra ngược vào AST node
            node.var_type = kieu_khai_bao

    # -------------------------------------------------------------------------
    # Câu lệnh điều khiển
    # -------------------------------------------------------------------------

    def visit_if_stmt(self, node: "IfStmt", o: Any = None):
        kieu_dk = self.duyet_expr(node.condition, o)

        # Nếu điều kiện là auto identifier -> suy ra int
        if isinstance(kieu_dk, AutoType):
            if isinstance(node.condition, Identifier):
                self.cap_nhat_kieu_auto(node.condition.name, IntType(), o["env"])
                kieu_dk = IntType()
            else:
                raise TypeMismatchInStatement(node)

        if not isinstance(kieu_dk, IntType):
            raise TypeMismatchInStatement(node)

        # Duyệt nhánh then
        ctx_then = dict(o)
        if isinstance(node.then_stmt, VarDecl):
            ctx_then["env"] = Env(cha=o["env"])
            self.visit_var_decl(node.then_stmt, ctx_then)
        else:
            self.duyet_stmt(node.then_stmt, ctx_then)

        # Duyệt nhánh else (nếu có)
        if node.else_stmt is not None:
            ctx_else = dict(o)
            if isinstance(node.else_stmt, VarDecl):
                ctx_else["env"] = Env(cha=o["env"])
                self.visit_var_decl(node.else_stmt, ctx_else)
            else:
                self.duyet_stmt(node.else_stmt, ctx_else)

    def visit_while_stmt(self, node: "WhileStmt", o: Any = None):
        kieu_dk = self.duyet_expr(node.condition, o)

        if isinstance(kieu_dk, AutoType):
            if isinstance(node.condition, Identifier):
                self.cap_nhat_kieu_auto(node.condition.name, IntType(), o["env"])
                kieu_dk = IntType()
            else:
                raise TypeMismatchInStatement(node)

        if not isinstance(kieu_dk, IntType):
            raise TypeMismatchInStatement(node)
        ctx_loop = dict(o, in_loop=True)
        if isinstance(node.body, VarDecl):
            ctx_loop["env"] = Env(cha=o["env"])
            self.visit_var_decl(node.body, ctx_loop)
        else:
            self.duyet_stmt(node.body, ctx_loop)

        o["return_type"] = ctx_loop["return_type"]

    def visit_for_stmt(self, node: "ForStmt", o: Any = None):
        scope_ngoai = o["env"]
        if node.init is not None:
            if isinstance(node.init, VarDecl):
                self.visit_var_decl(node.init, o)
                # Không ép auto -> int; để body suy ra kiểu
            else:
                bieu_thuc_init = node.init.expr if isinstance(node.init, ExprStmt) else node.init
                self.duyet_expr(bieu_thuc_init, o)

        scope_for = Env(cha=scope_ngoai)
        ctx_for = dict(o, env=scope_for, in_loop=True)

        # --- Phần condition ---
        if node.condition is not None:
            kieu_cond = self.duyet_expr(node.condition, ctx_for)
            if isinstance(kieu_cond, AutoType):
                if isinstance(node.condition, Identifier):
                    self.cap_nhat_kieu_auto(node.condition.name, IntType(), scope_for)
                    kieu_cond = IntType()
                else:
                    raise TypeMismatchInStatement(node)
            if not isinstance(kieu_cond, IntType):
                raise TypeMismatchInStatement(node)

        # --- Phần update ---
        if node.update is not None:
            self.duyet_expr(node.update, ctx_for)

        # --- Body ---
        if isinstance(node.body, VarDecl):
            ctx_body = dict(ctx_for, env=Env(cha=scope_for))
            self.visit_var_decl(node.body, ctx_body)
        else:
            self.duyet_stmt(node.body, ctx_for)

        o["return_type"] = ctx_for["return_type"]

    def visit_switch_stmt(self, node: "SwitchStmt", o: Any = None):
        kieu_bieu_thuc = self.duyet_expr(node.expr, o)

        if isinstance(kieu_bieu_thuc, AutoType):
            if isinstance(node.expr, Identifier):
                self.cap_nhat_kieu_auto(node.expr.name, IntType(), o["env"])
                kieu_bieu_thuc = IntType()
            else:
                raise TypeMismatchInStatement(node)

        if not isinstance(kieu_bieu_thuc, IntType):
            raise TypeMismatchInStatement(node)

        scope_switch = Env(cha=o["env"])
        auto_vars_switch = []
        ctx_switch = dict(o,
                          env=scope_switch,
                          in_switch=True,
                          switch_node=node,
                          auto_vars=auto_vars_switch)

        for case in node.cases:
            self.visit_case_stmt(case, ctx_switch)

        if node.default_case is not None:
            self.visit_default_stmt(node.default_case, ctx_switch)

        # Kiểm tra auto vars trong switch
        for (bien_auto, scope_auto) in auto_vars_switch:
            if isinstance(scope_auto.lookup(bien_auto.name), AutoType):
                raise TypeCannotBeInferred(node)

        o["return_type"] = ctx_switch["return_type"]

    def hang_so_nguyen(self, bieu_thuc) -> bool:
        if isinstance(bieu_thuc, IntLiteral):
            return True
        if isinstance(bieu_thuc, FloatLiteral):
            return False
        if isinstance(bieu_thuc, (Identifier, FuncCall, MemberAccess, StructLiteral)):
            return False
        if isinstance(bieu_thuc, PrefixOp):
            return self.hang_so_nguyen(bieu_thuc.operand)
        if isinstance(bieu_thuc, BinaryOp):
            return (self.hang_so_nguyen(bieu_thuc.left)
                    and self.hang_so_nguyen(bieu_thuc.right))
        return False

    def visit_case_stmt(self, node: "CaseStmt", o: Any = None):
        """Case trong switch: giá trị case phải là hằng số nguyên."""
        kieu_case = self.duyet_expr(node.expr, o)

        # Nếu auto thì không hợp lệ cho case
        if isinstance(kieu_case, AutoType):
            raise TypeMismatchInStatement(o.get("switch_node", node))

        # Phải là hằng số nguyên (không phải biến, không phải float)
        if not self.hang_so_nguyen(node.expr):
            node_switch = o.get("switch_node")
            raise TypeMismatchInStatement(node_switch if node_switch is not None else node)

        if not isinstance(kieu_case, IntType):
            node_switch = o.get("switch_node")
            raise TypeMismatchInStatement(node_switch if node_switch is not None else node)

        # Duyệt các câu lệnh trong case
        for stmt in node.statements:
            self.duyet_stmt(stmt, o)

    def visit_default_stmt(self, node: "DefaultStmt", o: Any = None):
        for stmt in node.statements:
            self.duyet_stmt(stmt, o)

    def visit_break_stmt(self, node: "BreakStmt", o: Any = None):
        """break chỉ được dùng trong loop hoặc switch."""
        if not o.get("in_loop", False) and not o.get("in_switch", False):
            raise MustInLoop(node)

    def visit_continue_stmt(self, node: "ContinueStmt", o: Any = None):
        """continue chỉ được dùng trong loop (switch không tính)."""
        if not o.get("in_loop", False):
            raise MustInLoop(node)

    def visit_return_stmt(self, node: "ReturnStmt", o: Any = None):
        """Câu lệnh return.
        
        TH1: return; -> hàm phải void (hoặc auto chưa biết -> suy ra void)
        TH2: return expr; -> kiểu expr phải khớp kiểu trả về hàm
        """
        kieu_tra_ve_ham = o["return_type"]

        if node.expr is None:
            # return không có giá trị
            if isinstance(kieu_tra_ve_ham, AutoType):
                o["return_type"] = VoidType()   # suy ra hàm trả về void
            elif not isinstance(kieu_tra_ve_ham, VoidType):
                raise TypeMismatchInStatement(node)
        else:
            # return có giá trị
            if isinstance(kieu_tra_ve_ham, AutoType):
                # Suy kiểu trả về từ biểu thức return
                kieu_expr = self.duyet_expr(node.expr, o)
                if isinstance(kieu_expr, AutoType):
                    raise TypeCannotBeInferred(node)
                o["return_type"] = kieu_expr
            else:
                # Kiểu trả về đã biết, kiểm tra khớp
                if isinstance(kieu_tra_ve_ham, VoidType):
                    raise TypeMismatchInStatement(node)
                kieu_expr = self.duyet_expr(node.expr, o)
                if isinstance(kieu_expr, AutoType):
                    raise TypeCannotBeInferred(node.expr)
                if not types_equal(kieu_expr, kieu_tra_ve_ham):
                    raise TypeMismatchInStatement(node)

    def visit_expr_stmt(self, node: "ExprStmt", o: Any = None):
        if isinstance(node.expr, AssignExpr):
            # Kiểm tra xem lhs hoặc rhs có auto không
            scope: Env = o["env"]
            lhs_is_auto = False
            if isinstance(node.expr.lhs, Identifier):
                kieu_lhs = scope.lookup(node.expr.lhs.name)
                lhs_is_auto = isinstance(kieu_lhs, AutoType)

            rhs_is_assign = isinstance(node.expr.rhs, AssignExpr)

            if lhs_is_auto or rhs_is_assign:
                kieu_ket_qua = self.duyet_expr(node.expr, o)
            else:
                try:
                    kieu_ket_qua = self.duyet_expr(node.expr, o)
                except TypeMismatchInExpression:
                    raise TypeMismatchInStatement(node)
        else:
            kieu_ket_qua = self.duyet_expr(node.expr, o)

        if isinstance(kieu_ket_qua, AutoType):
            toan_hang_auto = getattr(node.expr, "_auto_operands", None)
            if toan_hang_auto is None:
                raise TypeCannotBeInferred(node.expr)
            kieu_da_biet = getattr(node.expr, "_known_type", None)
            if isinstance(kieu_da_biet, FloatType):
                raise TypeCannotBeInferred(node.expr)
            known_side_is_typed = False
            for operand in toan_hang_auto:
                if isinstance(operand, Identifier):
                    kieu_op = o["env"].lookup(operand.name)
                    if kieu_op is not None and not isinstance(kieu_op, AutoType):
                        known_side_is_typed = True
                        break
                elif not isinstance(operand, IntLiteral):
                    # FuncCall, MemberAccess, BinaryOp, FloatLiteral, StringLiteral, v.v.
                    known_side_is_typed = True
                    break
            if known_side_is_typed:
                raise TypeCannotBeInferred(node.expr)
            # else: defer — kiểu sẽ được suy ra sau (auto_vars check cuối block)

    def visit_assign_stmt(self, node, o: Any = None):
        """Dùng chung với assign expression."""
        return self.visit_assign_expr(node, o)

    # =========================================================================
    # PHẦN 5: Biểu thức (Expressions)
    # =========================================================================

    def duyet_expr(self, expr, o):
        if isinstance(expr, IntLiteral):
            return self.visit_int_literal(expr, o)
        elif isinstance(expr, FloatLiteral):
            return self.visit_float_literal(expr, o)
        elif isinstance(expr, StringLiteral):
            return self.visit_string_literal(expr, o)
        elif isinstance(expr, Identifier):
            return self.visit_identifier(expr, o)
        elif isinstance(expr, BinaryOp):
            return self.visit_binary_op(expr, o)
        elif isinstance(expr, PrefixOp):
            return self.visit_prefix_op(expr, o)
        elif isinstance(expr, PostfixOp):
            return self.visit_postfix_op(expr, o)
        elif isinstance(expr, AssignExpr):
            return self.visit_assign_expr(expr, o)
        elif isinstance(expr, MemberAccess):
            return self.visit_member_access(expr, o)
        elif isinstance(expr, FuncCall):
            return self.visit_func_call(expr, o)
        elif isinstance(expr, StructLiteral):
            return self.visit_struct_literal(expr, o)
        else:
            raise TypeMismatchInExpression(expr)

    # Các literal: trả về kiểu tương ứng
    def visit_int_literal(self, node: "IntLiteral", o: Any = None):
        return IntType()

    def visit_float_literal(self, node: "FloatLiteral", o: Any = None):
        return FloatType()

    def visit_string_literal(self, node: "StringLiteral", o: Any = None):
        return StringType()

    def visit_identifier(self, node: "Identifier", o: Any = None):
        scope: Env = o["env"]
        kieu = scope.lookup(node.name)
        if kieu is None:
            raise UndeclaredIdentifier(node.name)
        return kieu

    def visit_binary_op(self, node: "BinaryOp", o: Any = None):
        """Kiểm tra kiểu cho phép toán 2 ngôi.
        
        Quy tắc:
        - +, -, *, /: 2 vế phải là int/float. Nếu có float thì kết quả float.
          Nếu 1 vế là auto identifier + 1 vế là int/float literal -> suy vế auto thành int
          Nếu cả 2 vế auto -> trả về AUTO (không suy được)
          Nếu 1 vế là auto nhưng vế kia là float -> lỗi TypeCannotBeInferred
        - %: 2 vế phải là int
        - ==, !=, <, <=, >, >=: 2 vế phải là int/float, kết quả là int
        - &&, ||: 2 vế phải là int, kết quả là int
        """
        kieu_trai = self.duyet_expr(node.left, o)
        kieu_phai = self.duyet_expr(node.right, o)
        math = node.operator

        if math in ("+", "-", "*", "/"):
            # Trường hợp cả 2 đều auto: không suy được
            if isinstance(kieu_trai, AutoType) and isinstance(kieu_phai, AutoType):
                node._auto_operands = (node.left, node.right)
                return AUTO

            # Một vế auto, một vế đã biết
            if isinstance(kieu_trai, AutoType) or isinstance(kieu_phai, AutoType):
                node._auto_operands = (node.left, node.right)
                node._known_type = kieu_phai if isinstance(kieu_trai, AutoType) else kieu_trai
                return AUTO

            # Cả 2 đã biết kiểu, phải là số
            if not isinstance(kieu_trai, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            if not isinstance(kieu_phai, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)

            # Có float thì kết quả float, không thì int
            if isinstance(kieu_trai, FloatType) or isinstance(kieu_phai, FloatType):
                return FloatType()
            return IntType()

        elif math == "%":
            # Modulo: 2 vế phải là int
            if isinstance(kieu_trai, AutoType):
                if isinstance(node.left, Identifier):
                    self.cap_nhat_kieu_auto(node.left.name, IntType(), o["env"])
                    kieu_trai = IntType()
                else:
                    raise TypeCannotBeInferred(node.left)
            if isinstance(kieu_phai, AutoType):
                if isinstance(node.right, Identifier):
                    self.cap_nhat_kieu_auto(node.right.name, IntType(), o["env"])
                    kieu_phai = IntType()
                else:
                    raise TypeCannotBeInferred(node.right)
            if not isinstance(kieu_trai, IntType) or not isinstance(kieu_phai, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()

        elif math in ("==", "!=", "<", "<=", ">", ">="):
            # So sánh: 2 vế phải int hoặc float (không được auto)
            if isinstance(kieu_trai, AutoType) or isinstance(kieu_phai, AutoType):
                raise TypeCannotBeInferred(node)
            if (not isinstance(kieu_trai, (IntType, FloatType))
                    or not isinstance(kieu_phai, (IntType, FloatType))):
                raise TypeMismatchInExpression(node)
            return IntType()

        elif math in ("&&", "||"):
            # Logical: 2 vế phải int
            if isinstance(kieu_trai, AutoType):
                if isinstance(node.left, Identifier):
                    self.cap_nhat_kieu_auto(node.left.name, IntType(), o["env"])
                    kieu_trai = IntType()
                else:
                    raise TypeCannotBeInferred(node.left)
            if isinstance(kieu_phai, AutoType):
                if isinstance(node.right, Identifier):
                    self.cap_nhat_kieu_auto(node.right.name, IntType(), o["env"])
                    kieu_phai = IntType()
                else:
                    raise TypeCannotBeInferred(node.right)
            if not isinstance(kieu_trai, IntType) or not isinstance(kieu_phai, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()

        else:
            raise TypeMismatchInExpression(node)

    def visit_prefix_op(self, node: "PrefixOp", o: Any = None):
        """ ++, --, !, +, -"""
        math = node.operator

        if math in ("++", "--"):
            if not isinstance(node.operand, (Identifier, MemberAccess)):
                raise TypeMismatchInExpression(node)
            kieu_toan_hang = self.duyet_expr(node.operand, o)
            # Auto identifier -> suy thành int
            if isinstance(kieu_toan_hang, AutoType):
                if isinstance(node.operand, Identifier):
                    self.cap_nhat_kieu_auto(node.operand.name, IntType(), o["env"])
                    kieu_toan_hang = IntType()
                else:
                    raise TypeMismatchInExpression(node)
            if not isinstance(kieu_toan_hang, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()

        elif math == "!":
            # NOT: toán hạng phải là int
            kieu_toan_hang = self.duyet_expr(node.operand, o)
            if isinstance(kieu_toan_hang, AutoType):
                if isinstance(node.operand, Identifier):
                    self.cap_nhat_kieu_auto(node.operand.name, IntType(), o["env"])
                    kieu_toan_hang = IntType()
                else:
                    raise TypeMismatchInExpression(node)
            if not isinstance(kieu_toan_hang, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()

        elif math in ("-", "+"):
            # Dấu âm/dương: toán hạng phải là số, không suy auto được
            kieu_toan_hang = self.duyet_expr(node.operand, o)
            if isinstance(kieu_toan_hang, AutoType):
                raise TypeCannotBeInferred(node)
            if not isinstance(kieu_toan_hang, (IntType, FloatType)):
                raise TypeMismatchInExpression(node)
            return kieu_toan_hang

        else:
            raise TypeMismatchInExpression(node)

    def visit_postfix_op(self, node: "PostfixOp", o: Any = None):
        if node.operator not in ("++", "--"):
            raise TypeMismatchInExpression(node)
        if not isinstance(node.operand, (Identifier, MemberAccess)):
            raise TypeMismatchInExpression(node)

        kieu_toan_hang = self.duyet_expr(node.operand, o)
        if isinstance(kieu_toan_hang, AutoType):
            if isinstance(node.operand, Identifier):
                self.cap_nhat_kieu_auto(node.operand.name, IntType(), o["env"])
                kieu_toan_hang = IntType()
            else:
                raise TypeMismatchInExpression(node)
        if not isinstance(kieu_toan_hang, IntType):
            raise TypeMismatchInExpression(node)
        return IntType()

    def visit_assign_expr(self, node: "AssignExpr", o: Any = None):
        """Biểu thức gán: lhs = rhs
        Nếu lhs là auto -> suy kiểu từ rhs.
        Nếu rhs là auto -> suy kiểu ngược từ lhs.
        """
        if not isinstance(node.lhs, (Identifier, MemberAccess)):
            raise TypeMismatchInExpression(node)
        scope: Env = o["env"]
        
        # Lấy kiểu vế trái
        if isinstance(node.lhs, Identifier):
            kieu_trai = scope.lookup(node.lhs.name)
            if kieu_trai is None:
                raise UndeclaredIdentifier(node.lhs.name)
        else:
            kieu_trai = self.duyet_expr(node.lhs, o)

        # Lấy kiểu vế phải
        kieu_phai = self.duyet_expr(node.rhs, o)

        if isinstance(kieu_trai, AutoType):
            # lhs là auto, suy từ rhs
            if isinstance(kieu_phai, AutoType):
                # Cả 2 đều auto 
                if isinstance(node.lhs, Identifier):
                    raise TypeCannotBeInferred(node)
                else:
                    raise TypeMismatchInExpression(node)
            if isinstance(node.lhs, Identifier):
                self.cap_nhat_kieu_auto(node.lhs.name, kieu_phai, scope)
                kieu_trai = kieu_phai
            else:
                raise TypeMismatchInExpression(node)
        else:
            if isinstance(kieu_phai, AutoType):
                # rhs là auto, suy ngược từ lhs
                if isinstance(node.rhs, Identifier):
                    self.cap_nhat_kieu_auto(node.rhs.name, kieu_trai, scope)
                    kieu_phai = kieu_trai
                else:
                    raise TypeCannotBeInferred(node.rhs)
            if not _is_assignable(kieu_trai, kieu_phai):
                raise TypeMismatchInExpression(node)

        return kieu_trai

    def cap_nhat_kieu_auto(self, ten_bien: str, kieu_moi, scope: Env):
        scope_hien_tai = scope
        while scope_hien_tai is not None:
            if ten_bien in scope_hien_tai.bang:
                scope_hien_tai.bang[ten_bien] = kieu_moi
                return
            scope_hien_tai = scope_hien_tai.parent

    def visit_member_access(self, node: "MemberAccess", o: Any = None):
        kieu_obj = self.duyet_expr(node.obj, o)

        # obj phải là struct, không được là auto hoặc các kiểu khác
        if isinstance(kieu_obj, AutoType) or not isinstance(kieu_obj, StructType):
            raise TypeMismatchInExpression(node)

        bang_struct = o["structs"]
        if kieu_obj.struct_name not in bang_struct:
            raise TypeMismatchInExpression(node)

        # Tìm field trong struct
        danh_sach_field = bang_struct[kieu_obj.struct_name]
        for field in danh_sach_field:
            if field.name == node.member:
                return field.member_type

        # Field không tồn tại
        raise TypeMismatchInExpression(node)

    def visit_func_call(self, node: "FuncCall", o: Any = None):
        bang_ham = o["funcs"]

        if node.name not in bang_ham:
            raise UndeclaredFunction(node.name)

        danh_sach_kieu_param, kieu_tra_ve = bang_ham[node.name]
        if isinstance(kieu_tra_ve, AutoType):
            kieu_hien_tai = o.get("return_type")
            if kieu_hien_tai is not None and not isinstance(kieu_hien_tai, AutoType):
                kieu_tra_ve = kieu_hien_tai

        # Kiểm tra số lượng argument
        if len(node.args) != len(danh_sach_kieu_param):
            raise TypeMismatchInExpression(node)

        # Kiểm tra từng argument
        for arg, kieu_param in zip(node.args, danh_sach_kieu_param):
            kieu_arg = self.duyet_expr(arg, o)
            if isinstance(kieu_arg, AutoType):
                if isinstance(arg, Identifier):
                    self.cap_nhat_kieu_auto(arg.name, kieu_param, o["env"])
                    kieu_arg = kieu_param
                else:
                    raise TypeCannotBeInferred(arg)
            if not types_equal(kieu_arg, kieu_param):
                raise TypeMismatchInExpression(node)

        return kieu_tra_ve

    def kiem_tra_struct_literal(self, node, kieu_khai_bao, decl_node, o):
        if not isinstance(kieu_khai_bao, StructType):
            raise TypeMismatchInExpression(node)

        bang_struct = o["structs"]
        if kieu_khai_bao.struct_name not in bang_struct:
            raise UndeclaredStruct(kieu_khai_bao.struct_name)

        danh_sach_field = bang_struct[kieu_khai_bao.struct_name]

        
        if len(node.values) != len(danh_sach_field):
            raise TypeMismatchInExpression(node)

        # Kiểm tra từng giá trị
        for gia_tri, field in zip(node.values, danh_sach_field):
            kieu_giatri = self.duyet_expr(gia_tri, o)
            if isinstance(kieu_giatri, AutoType):
                if isinstance(gia_tri, Identifier):
                    self.cap_nhat_kieu_auto(gia_tri.name, field.member_type, o["env"])
                else:
                    raise TypeMismatchInExpression(node)
            elif not types_equal(kieu_giatri, field.member_type):
                raise TypeMismatchInExpression(node)

    def visit_struct_literal(self, node, o=None):
        for gia_tri in node.values:
            self.duyet_expr(gia_tri, o)
        return node

    # =========================================================================
    #  Alias return it  ASTVisitor 
    # =========================================================================

    # Một số visitor framework 
    def _visit_expr(self, expr, o):
        return self.duyet_expr(expr, o)

    def _visit_stmt(self, stmt, o):
        return self.duyet_stmt(stmt, o)