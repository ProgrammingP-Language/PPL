"""
AST Generation module for TyC programming language.
This module contains the ASTGeneration class that converts parse trees
into Abstract Syntax Trees using the visitor pattern.
"""

from functools import reduce
from build.TyCVisitor import TyCVisitor
from build.TyCParser import TyCParser
from src.utils.nodes import *

class ASTGeneration(TyCVisitor):

    # PROGRAM 
    # program: (struct_decl | func_decl)* EOF;
    def visitProgram(self, ctx):
        result = []
        for child in ctx.children or []:
            from antlr4 import TerminalNode
            if isinstance(child, TerminalNode):
                continue
            result.append(self.visit(child))
        return Program(result)
    
    # STRUCT 
    # struct_decl: STRUCT ID LBRACE struct_field* RBRACE SEMI;
    def visitStruct_decl(self, ctx):
        name = ctx.ID().getText()
        members = []
        
        if ctx.struct_field():
            for field in ctx.struct_field():
                members.append(self.visit(field))
        return StructDecl(name, members)
    
    # struct_field: param_type ID SEMI;
    def visitStruct_field(self, ctx):
        typ = self.visit(ctx.param_type())
        name = ctx.ID().getText()
        return MemberDecl(typ, name)
    
    # FUNCTION
    # func_decl: return_type? ID LPAREN param_list? RPAREN block;
    def visitFunc_decl(self, ctx):
        if ctx.return_type():
            ret_type = self.visit(ctx.return_type())
        else:
            ret_type = None
        name = ctx.ID().getText()
        params = self.visit(ctx.param_list()) if ctx.param_list() else []
        body = self.visit(ctx.block())
        return FuncDecl(ret_type, name, params, body)

    # param_list
    def visitParam_list(self, ctx):
        return [self.visit(p) for p in ctx.param()]

    # param: param_type ID
    def visitParam(self, ctx):
        return Param(self.visit(ctx.param_type()), ctx.ID().getText())

    # TYPE 
    # return_type: INT | FLOAT | STRING | VOID | ID;
    def visitReturn_type(self, ctx):
        if ctx.INT():
            return IntType()
        if ctx.FLOAT():
            return FloatType()
        if ctx.STRING():
            return StringType()
        if ctx.VOID():
            return VoidType()
        if ctx.ID():
            return StructType(ctx.ID().getText())
        return None

    # param_type: INT | FLOAT | STRING | ID;
    def visitParam_type(self, ctx):
        if ctx.INT():
            return IntType()
        if ctx.FLOAT():
            return FloatType()
        if ctx.STRING():
            return StringType()
        if ctx.ID():
            return StructType(ctx.ID().getText())
        return None
    
    # var_type: INT | FLOAT | STRING | AUTO | ID;
    def visitVar_type(self, ctx):
        if ctx.INT():
            return IntType()
        if ctx.FLOAT():
            return FloatType()
        if ctx.STRING():
            return StringType()
        if ctx.AUTO():
            return None  # Return None for auto
        if ctx.ID():
            return StructType(ctx.ID().getText())
        return None

    # BLOCK 
    # block: LBRACE statement* RBRACE;
    def visitBlock(self, ctx):
        stmts = []
        for s in ctx.statement():
            stmt = self.visit(s)
            if stmt is not None:
                stmts.append(stmt)
        return BlockStmt(stmts)

    # STATEMENT 
    def visitStatement(self, ctx):
        if ctx.var_decl():
            return self.visit(ctx.var_decl())
        if ctx.expr_stmt():
            return self.visit(ctx.expr_stmt())
        if ctx.if_stmt():
            return self.visit(ctx.if_stmt())
        if ctx.while_stmt():
            return self.visit(ctx.while_stmt())
        if ctx.for_stmt():
            return self.visit(ctx.for_stmt())
        if ctx.switch_stmt():
            return self.visit(ctx.switch_stmt())
        if ctx.return_stmt():
            return self.visit(ctx.return_stmt())
        if ctx.break_stmt():
            return self.visit(ctx.break_stmt())
        if ctx.continue_stmt():
            return self.visit(ctx.continue_stmt())
        if ctx.block():
            return self.visit(ctx.block())
        return None

    # non_empty_statement (same as statement)
    def visitNon_empty_statement(self, ctx):
        return self.visitStatement(ctx)

    # var_decl: var_type ID (ASSIGN expression)?;
    def visitVar_decl(self, ctx):
        typ = self.visit(ctx.var_type())
        name = ctx.ID().getText()
        value = self.visit(ctx.expression()) if ctx.expression() else None
        return VarDecl(typ, name, value)

    # expr_stmt: expression;
    def visitExpr_stmt(self, ctx):
        return ExprStmt(self.visit(ctx.expression()))

    # return_stmt: RETURN expression?;
    def visitReturn_stmt(self, ctx):
        val = self.visit(ctx.expression()) if ctx.expression() else None
        return ReturnStmt(val)
    
    # break_stmt: BREAK;
    def visitBreak_stmt(self, ctx):
        return BreakStmt()
    
    # continue_stmt: CONTINUE;
    def visitContinue_stmt(self, ctx):
        return ContinueStmt()

    # switch_stmt: SWITCH LPAREN expression RPAREN LBRACE switch_body RBRACE;
    def visitSwitch_stmt(self, ctx):
        expr = self.visit(ctx.expression())
        cases, default_case = self.visit(ctx.switch_body())
        return SwitchStmt(expr, cases, default_case)
    
    def visitSwitch_body(self, ctx):
        cases = []
        default_case = None
        if ctx.case_clause():
            for c in ctx.case_clause():
                cases.append(self.visit(c))
        if ctx.default_clause():
            default_case = self.visit(ctx.default_clause())
        return cases, default_case

    # case_clause: CASE expression COLON statement*;
    def visitCase_clause(self, ctx):
        expr = self.visit(ctx.expression())
        stmts = []
        if ctx.statement():
            for s in ctx.statement():
                stmt = self.visit(s)
                if stmt is not None:
                    stmts.append(stmt)
        return CaseStmt(expr, stmts)

    # default_clause: DEFAULT COLON statement*;
    def visitDefault_clause(self, ctx):
        stmts = []
        if ctx.statement():
            for s in ctx.statement():
                stmt = self.visit(s)
                if stmt is not None:
                    stmts.append(stmt)
        return DefaultStmt(stmts)

    # CONTROL FLOW 
    # if_stmt: IF LPAREN expression RPAREN non_empty_statement (ELSE non_empty_statement)?;
    def visitIf_stmt(self, ctx):
        cond = self.visit(ctx.expression())
        then_stmt = self.visit(ctx.non_empty_statement(0))
        else_stmt = self.visit(ctx.non_empty_statement(1)) if ctx.ELSE() else None
        return IfStmt(cond, then_stmt, else_stmt)

    # while_stmt: WHILE LPAREN expression RPAREN non_empty_statement;
    def visitWhile_stmt(self, ctx):
        return WhileStmt(
            self.visit(ctx.expression()),
            self.visit(ctx.non_empty_statement())
        )

    # for_stmt: FOR LPAREN for_init SEMI expression? SEMI for_update? RPAREN non_empty_statement;
    def visitFor_stmt(self, ctx):
        init = self.visit(ctx.for_init()) if ctx.for_init() else None
        cond = self.visit(ctx.expression()) if ctx.expression() else None
        update = self.visit(ctx.for_update()) if ctx.for_update() else None
        body = self.visit(ctx.non_empty_statement())
        return ForStmt(init, cond, update, body)

    # for_init: var_decl | lhs ASSIGN expression | ;
    def visitFor_init(self, ctx):
        if ctx.var_decl():
            return self.visit(ctx.var_decl())
        if ctx.lhs():
            lhs = self.visit(ctx.lhs())
            rhs = self.visit(ctx.expression())
            return ExprStmt(AssignExpr(lhs, rhs))
        return None

    # for_update: lhs ASSIGN expression | (INCREMENT | DECREMENT)+ postfix (INCREMENT | DECREMENT)* | postfix (INCREMENT | DECREMENT)+ | func_call;
    def visitFor_update(self, ctx):
        if ctx.func_call():
            return self.visit(ctx.func_call())
        if ctx.ASSIGN():
            lhs = self.visit(ctx.lhs())
            rhs = self.visit(ctx.expression())
            return AssignExpr(lhs, rhs)
        if ctx.postfix():
            var = self.visit(ctx.postfix())
            first_child_text = ctx.getChild(0).getText()
            if first_child_text in ('++', '--'):
                # Prefix: (INCREMENT | DECREMENT)+ postfix (INCREMENT | DECREMENT)*
                prefix_ops = []
                postfix_ops = []
                found_postfix = False
                for i in range(ctx.getChildCount()):
                    t = ctx.getChild(i).getText()
                    if t in ('++', '--'):
                        if found_postfix:
                            postfix_ops.append(t)
                        else:
                            prefix_ops.append(t)
                    else:
                        found_postfix = True
                result = var
                for op in postfix_ops:
                    result = PostfixOp(op, result)
                for op in reversed(prefix_ops):
                    result = PrefixOp(op, result)
                return result
            else:
                # Postfix: postfix (INCREMENT | DECREMENT)+
                ops = []
                for i in range(1, ctx.getChildCount()):
                    t = ctx.getChild(i).getText()
                    if t in ('++', '--'):
                        ops.append(t)
                result = var
                for op in ops:
                    result = PostfixOp(op, result)
                return result
        return None

    # lhs: ID (DOT ID)* | (func_call | LPAREN expression RPAREN | struct_init | literal) (DOT ID)+
    def visitLhs(self, ctx):
        # Check for the first alternative: ID (DOT ID)*
        ids = ctx.ID()
        if ids and not ctx.func_call() and not ctx.expression() and not ctx.struct_init() and not ctx.literal():
            # First alternative: ID (DOT ID)*
            if len(ids) == 1:
                return Identifier(ids[0].getText())
            else:
                # Build member access chain
                result = Identifier(ids[0].getText())
                for i in range(1, len(ids)):
                    result = MemberAccess(result, ids[i].getText())
                return result
        
        # Second alternative: (func_call | LPAREN expression RPAREN | struct_init | literal) (DOT ID)+
        base = None
        if ctx.func_call():
            base = self.visit(ctx.func_call())
        elif ctx.expression():
            base = self.visit(ctx.expression())
        elif ctx.struct_init():
            base = self.visit(ctx.struct_init())
        elif ctx.literal():
            base = self.visit(ctx.literal())
        
        if base and ids:
            # Apply DOT ID+ to base
            result = base
            for id_node in ids:
                result = MemberAccess(result, id_node.getText())
            return result
        
        return base

    # EXPRESSION 
    # expression: assignment;
    def visitExpression(self, ctx):
        return self.visit(ctx.assignment())

    # assignment: lhs ASSIGN assignment | logical_or;
    def visitAssignment(self, ctx):
        if ctx.ASSIGN():
            lhs = self.visit(ctx.lhs())
            rhs = self.visit(ctx.assignment())
            return AssignExpr(lhs, rhs)
        return self.visit(ctx.logical_or())

    def visitLogical_or(self, ctx):
        left = self.visit(ctx.logical_and(0))
        for i in range(1, len(ctx.logical_and())):
            left = BinaryOp(left, "||", self.visit(ctx.logical_and(i)))
        return left

    def visitLogical_and(self, ctx):
        left = self.visit(ctx.equality(0))
        for i in range(1, len(ctx.equality())):
            left = BinaryOp(left, "&&", self.visit(ctx.equality(i)))
        return left

    def visitEquality(self, ctx):
        left = self.visit(ctx.relational(0))
        for i in range(1, len(ctx.relational())):
            op = ctx.getChild(2 * i - 1).getText()
            left = BinaryOp(left, op, self.visit(ctx.relational(i)))
        return left

    def visitRelational(self, ctx):
        left = self.visit(ctx.additive(0))
        for i in range(1, len(ctx.additive())):
            op = ctx.getChild(2 * i - 1).getText()
            left = BinaryOp(left, op, self.visit(ctx.additive(i)))
        return left

    def visitAdditive(self, ctx):
        left = self.visit(ctx.multiplicative(0))
        for i in range(1, len(ctx.multiplicative())):
            op = ctx.getChild(2 * i - 1).getText()
            left = BinaryOp(left, op, self.visit(ctx.multiplicative(i)))
        return left

    def visitMultiplicative(self, ctx):
        left = self.visit(ctx.unary(0))
        for i in range(1, len(ctx.unary())):
            op = ctx.getChild(2 * i - 1).getText()
            left = BinaryOp(left, op, self.visit(ctx.unary(i)))
        return left

    # unary:
    #     : (NOT | PLUS | MINUS) unary
    #     | (INCREMENT | DECREMENT)+ postfix (INCREMENT | DECREMENT)*
    #     | postfix (INCREMENT | DECREMENT)+
    #     | postfix
    def visitUnary(self, ctx):
        # Alternative 1: (NOT | PLUS | MINUS) unary
        if ctx.unary():
            op = ctx.getChild(0).getText()  # '!', '+', or '-'
            return PrefixOp(op, self.visit(ctx.unary()))

        # Alternatives 2-4 have postfix
        if not ctx.postfix():
            return None

        postfix_node = self.visit(ctx.postfix())

        # Collect all increment/decrement operators and their positions
        prefix_ops = []
        postfix_ops = []
        found_postfix = False
        
        for i in range(ctx.getChildCount()):
            child_text = ctx.getChild(i).getText()
            if child_text in ('++', '--'):
                if found_postfix:
                    postfix_ops.append(child_text)
                else:
                    prefix_ops.append(child_text)
            else:
                # This is the postfix node
                found_postfix = True

        # Alternative 4: just postfix (no operators)
        if not prefix_ops and not postfix_ops:
            return postfix_node

        # Build the result
        result = postfix_node
        
        # Apply postfix operators (left to right)
        for op in postfix_ops:
            result = PostfixOp(op, result)
        
        # Apply prefix operators (right to left, so reverse)
        for op in reversed(prefix_ops):
            result = PrefixOp(op, result)

        return result

    # postfix: primary (DOT ID)*;
    def visitPostfix(self, ctx):
        base = self.visit(ctx.primary())
        
        # Check for DOT ID*
        ids = ctx.ID()
        if ids:
            result = base
            for id_node in ids:
                result = MemberAccess(result, id_node.getText())
            return result
        
        return base

    # primary: literal | member_access | func_call | LPAREN expression RPAREN | struct_init;
    def visitPrimary(self, ctx):
        if ctx.literal():
            return self.visit(ctx.literal())
        
        if ctx.struct_init():
            return self.visit(ctx.struct_init())
        
        if ctx.func_call():
            return self.visit(ctx.func_call())
        
        if ctx.member_access():
            return self.visit(ctx.member_access())
        
        if ctx.expression():
            return self.visit(ctx.expression())
        
        return None
    
    # member_access: ID (DOT ID)*;
    def visitMember_access(self, ctx):
        ids = ctx.ID()
        if len(ids) == 1:
            # Just a simple identifier
            return Identifier(ids[0].getText())
        else:
            # Member access chain: a.b.c
            result = Identifier(ids[0].getText())
            for i in range(1, len(ids)):
                result = MemberAccess(result, ids[i].getText())
            return result
    
    # func_call: ID LPAREN arg_list? RPAREN;
    def visitFunc_call(self, ctx):
        name = ctx.ID().getText()
        args = self.visit(ctx.arg_list()) if ctx.arg_list() else []
        return FuncCall(name, args)
    
    # arg_list: expression (COMMA expression)*;
    def visitArg_list(self, ctx):
        return [self.visit(e) for e in ctx.expression()]

    # struct_init: LBRACE arg_list? RBRACE;
    def visitStruct_init(self, ctx):
        args = self.visit(ctx.arg_list()) if ctx.arg_list() else []
        return StructLiteral(args)

    # LITERAL 
    # literal: INT_LIT | FLOAT_LIT | STRING_LIT;
    def visitLiteral(self, ctx):
        if ctx.INT_LIT():
            return IntLiteral(int(ctx.INT_LIT().getText()))
        if ctx.FLOAT_LIT():
            return FloatLiteral(float(ctx.FLOAT_LIT().getText()))
        if ctx.STRING_LIT():
            return StringLiteral(ctx.STRING_LIT().getText())
        return None