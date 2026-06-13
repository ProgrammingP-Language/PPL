grammar TyC;

@lexer::header {
from lexererr import *
}

@lexer::members {
def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:       
        result = super().emit();
        raise UncloseString(result.text);
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit();
        raise IllegalEscape(result.text);
    elif tk == self.ERROR_CHAR:
        result = super().emit();
        raise ErrorToken(result.text); 
    else:
        return super().emit();
}

options{
	language=Python3;
}
// ================= PARSER =================

//PROGRAM
program: (struct_decl | func_decl)* EOF;

//STRUCT 
struct_decl: STRUCT ID LBRACE struct_field* RBRACE SEMI;
struct_field: param_type ID SEMI;

//FUNCTION 
func_decl: return_type? ID LPAREN param_list? RPAREN block;
param_list: param (COMMA param)*;
param: param_type ID;

//TYPE 
type_spec: INT | FLOAT | STRING | VOID | AUTO | ID;
var_type: INT | FLOAT | STRING | AUTO | ID;
param_type: INT | FLOAT | STRING | ID;
return_type: INT | FLOAT | STRING | VOID | ID;

//BLOCK 
block: LBRACE statement* RBRACE; 

//STATEMENT 
statement
    : var_decl SEMI
    | if_stmt
    | while_stmt
    | for_stmt
    | switch_stmt
    | return_stmt SEMI
    | break_stmt SEMI
    | continue_stmt SEMI
    | block
    | expr_stmt SEMI
    ;

non_empty_statement
    : var_decl SEMI
    | if_stmt
    | while_stmt
    | for_stmt
    | switch_stmt
    | return_stmt SEMI
    | break_stmt SEMI
    | continue_stmt SEMI
    | block
    | expr_stmt SEMI
    ;

var_decl: var_type ID (ASSIGN expression)?;

lhs
    : ID (DOT ID)*
    | (func_call | LPAREN expression RPAREN | struct_init | literal) (DOT ID)+
    ;

if_stmt: IF LPAREN expression RPAREN non_empty_statement (ELSE non_empty_statement)?;

while_stmt: WHILE LPAREN expression RPAREN non_empty_statement ;

for_stmt: FOR LPAREN for_init SEMI expression? SEMI for_update? RPAREN non_empty_statement ;

for_init: var_decl | lhs ASSIGN expression |;

for_update: lhs ASSIGN expression | (INCREMENT | DECREMENT)+ postfix (INCREMENT | DECREMENT)* | postfix (INCREMENT | DECREMENT)+ | func_call;

return_stmt: RETURN expression?;

break_stmt: BREAK;

continue_stmt: CONTINUE;

expr_stmt: expression;

switch_stmt: SWITCH LPAREN expression RPAREN LBRACE switch_body RBRACE;

switch_body: 
    case_clause* default_clause case_clause*
    | case_clause+
    |
    ;

case_clause: CASE expression COLON statement*;

default_clause: DEFAULT COLON statement*;


//EXPRESSION 
expression: assignment;

assignment: lhs ASSIGN assignment | logical_or;

logical_or: logical_and (OR logical_and)*;

logical_and: equality (AND equality)*;

equality: relational ((EQ | NEQ) relational)*;

relational: additive ((LT | LE | GT | GE) additive)*;

additive: multiplicative ((PLUS | MINUS) multiplicative)*;

multiplicative: unary ((MUL | DIV | MOD) unary)*;

unary
    : (NOT | PLUS | MINUS) unary
    | (INCREMENT | DECREMENT)+ postfix (INCREMENT | DECREMENT)*
    | postfix (INCREMENT | DECREMENT)+
    | postfix
    ;

postfix: primary (DOT ID)* ;

primary: literal | member_access | func_call | LPAREN expression RPAREN | struct_init ;

member_access: ID (DOT ID)* ;

func_call: ID LPAREN arg_list? RPAREN ;

arg_list: expression (COMMA expression)*;

struct_init: LBRACE arg_list? RBRACE;

//LITERAL
literal: INT_LIT | FLOAT_LIT | STRING_LIT;

// ================= LEXER =================

//KEYWORDS 
STRUCT   : 'struct';
IF       : 'if';
ELSE     : 'else';
FOR      : 'for';
WHILE    : 'while';
RETURN   : 'return';
BREAK    : 'break';
CONTINUE : 'continue';
CASE     : 'case';
DEFAULT  : 'default';
INT      : 'int';
FLOAT    : 'float';
STRING   : 'string';
VOID     : 'void';
AUTO     : 'auto';
SWITCH   : 'switch';


//OPERATORS
INCREMENT : '++';
DECREMENT : '--';   
PLUS  : '+';
MINUS : '-';
MUL   : '*';
DIV   : '/';
MOD   : '%';
ASSIGN: '=';
EQ    : '==';
NEQ   : '!=';
LT    : '<';
LE    : '<=';
GT    : '>';
GE    : '>=';
AND   : '&&';
OR    : '||';
NOT   : '!';
DOT   : '.';

//SEPARATORS
LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
COMMA  : ',';
SEMI   : ';';
COLON  : ':';

//IDENTIFIER 
ID : [a-zA-Z_][a-zA-Z0-9_]*;

//NUMBER 
FLOAT_LIT
    : (
        ([0-9]+ '.' [0-9]*)
      | ('.' [0-9]+)
      | ([0-9]+ [eE] [+-]? [0-9]+)
      | ([0-9]+ '.' [0-9]* [eE] [+-]? [0-9]+)
      | ('.' [0-9]+ [eE] [+-]? [0-9]+)
      )
    ;

INT_LIT
    : [0-9]+
    ;


//STRING
UNCLOSE_STRING: '"' STR_CHAR* '\\'? ('\n' | '\r\n' | EOF) {
    if self.text[-1] == '\n' and len(self.text) >= 2 and self.text[-2] == '\r':
        self.text = self.text[1:-2]
    elif self.text[-1] == '\n':
        self.text = self.text[1:-1]
    else:
        self.text = self.text[1:]
};

ILLEGAL_ESCAPE: '"' STR_CHAR* '\\' ~[btnfr\\"] { self.text = self.text[1:] };

STRING_LIT: '"' STR_CHAR* '"' { self.text = self.text[1:-1] };

fragment STR_CHAR: ~[\r\n\\"] | ESC_SEQ;

fragment ESC_SEQ: '\\' [btnfr\\"];

//COMMENT & WS
LINE_COMMENT : '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
WS           : [ \t\r\n\f]+ -> skip;

//ERROR
ERROR_CHAR : . ;
