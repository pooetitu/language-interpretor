from genereTreeGraphviz2 import printTreeGraph

reserved = {
   'if' : 'IF',
   'print' : 'PRINT',
   'printString' : 'PRINT_STRING',
   'while' : 'WHILE',
   'for' : 'FOR',
   'functionValue' : "FONCTION_VALUE",
   'functionVoid' : "FONCTION_VOID",
   'return' : 'RETURN'
   }

tokens = [
    'STRING','NAME','NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 
    'AND', 'OR', 'EQUAL', 'LOWER','HIGHER',
    'LPAREN','RPAREN', 'LBRACKET','RBRACKET', 
    'COLON', 'COMMA',
    ]+list(reserved.values())

# Tokens
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t

def t_STRING(t):
    r'[\'"][^\'"\n]*[\'"]'
    t.type = reserved.get(t.value,'STRING')    # Check for reserved words
    return t

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET  = r'\{'
t_RBRACKET  = r'\}'
t_COLON = r';'
t_COMMA = r','
t_AND  = r'\&'
t_OR  = r'\|'
t_EQUAL  = r'=='
t_LOWER  = r'\<'
t_HIGHER  = r'\>'

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()


# Parsing rules
precedence = (
    ('left','PLUS','MINUS'),
    ('left','AND', 'OR', 'EQUAL', 'LOWER','HIGHER'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

 

def p_start(t):
    ''' start : linst'''
    t[0] = ('start',t[1])
    print(t[0])
    printTreeGraph(t[0])
    #eval(t[1])
    eval_inst(t[1])
    
def p_line(t):
    '''linst : linst inst 
            | inst '''
    if len(t)== 3 :
        t[0] = ('bloc',t[1], t[2])
    else:
        t[0] = ('bloc',t[1], 'empty')
    
def p_function_void_linst(t):
    '''linst_void : linst_void inst_void
            | inst_void '''
    if len(t) == 3 :
        t[0] = ('bloc',t[1], t[2])
    elif len:
        t[0] = ('bloc', t[1], 'empty')

def p_function_value_linst(t):
    '''linst_value : linst_value inst_value
        | linst_value return_value
        | return_value
        | inst_value'''
    if len(t) == 3:
        t[0] = ('bloc', t[1], t[2])
    else:
        t[0] = ('bloc', t[1], 'empty')

def p_params(t):
    '''params : NAME COMMA params
        | NAME '''
    if len(t) == 4 :
        t[0] = ('param', t[1], t[3])
    else:
        t[0] = ('param', t[1])


def p_function_call_params(t):
    '''call_params : expression COMMA call_params 
        | expression'''
    if len(t) == 4 :
        t[0] = ('param', t[1], t[3])
    else:
        t[0] = ('param', t[1])

def p_statement_function_value_definition(t):
    '''inst : FONCTION_VALUE NAME LPAREN params RPAREN LBRACKET linst_value RBRACKET
        | FONCTION_VALUE NAME LPAREN RPAREN LBRACKET linst_value RBRACKET'''
    if len(t) == 10:
        t[0] = ('function_value', t[2], t[4], t[7])
    else:
        t[0] = ('function_value', t[2], "empty", t[6])


def p_statement_function_void_definition(t):
    '''inst : FONCTION_VOID NAME LPAREN params RPAREN LBRACKET linst_void RBRACKET
        | FONCTION_VOID NAME LPAREN RPAREN LBRACKET linst_void RBRACKET'''
    if len(t) == 9:
        t[0] = ('function_void', t[2], t[4], t[7])
    else:
        t[0] = ('function_void', t[2], "empty", t[6])

def p_statement_return_value(t):
    '''return_value : RETURN expression COLON'''
    t[0] = ('return', t[2])

def p_statement_inst_value(t):
    '''inst_value : inst
    | return_value'''
    t[0] = t[1]

def p_statement_return_void(t):
    '''inst_void : RETURN COLON'''
    t[0] = ('return', 'empty')

def p_statement_inst_void(t):
    '''inst_void : inst'''
    t[0] = t[1]

def p_statement_if(t):
    'inst : IF LPAREN expression RPAREN LBRACKET linst RBRACKET'
    t[0] = ('if', t[3], t[6])

def p_statement_while(t):
    'inst : WHILE LPAREN expression RPAREN LBRACKET linst RBRACKET'
    t[0] = ('while', t[3], t[6])

def p_statement_for(t):
    'inst : FOR LPAREN inst expression COLON inst RPAREN LBRACKET linst RBRACKET'
    t[0] = ('for', t[3], t[4], t[6], t[9])

def p_statement_assign(t):
    'inst : NAME EQUALS expression COLON'
    t[0] = ('assign', t[1], t[3])

def p_statement_print(t):
    'inst : PRINT LPAREN expression RPAREN COLON'
    t[0] = ('print',t[3])

def p_statement_print_string(t):
    'inst : PRINT_STRING LPAREN STRING RPAREN COLON'
    t[0] = ('print_string',t[3])

def p_statement_incr(t):
    'inst : NAME PLUS PLUS COLON'
    t[0] = ('incr', t[1])

def p_statement_decr(t):
    'inst : NAME MINUS MINUS COLON'
    t[0] = ('decr', t[1])

def p_statement_plus_equal(t):
    'inst : NAME PLUS EQUALS expression COLON'
    t[0] = ('plus_equals', t[1], t[4])

def p_statement_minus_equal(t):
    'inst : NAME MINUS EQUALS expression COLON'
    t[0] = ('minus_equals', t[1], t[4])

def p_statement_function_void_call(t):
    '''inst : NAME LPAREN call_params RPAREN COLON
        | NAME LPAREN RPAREN COLON '''
    if len(t) == 6:
        t[0] = ('function_void_call', t[1], t[3])
    else:
        t[0] = ('function_void_call', t[1], "empty")

#def p_statement_expr(t):
#    'inst : expression COLON'
#
#    t[0] = t[1]



    
def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OR expression
                  | expression AND expression
                  | expression EQUAL expression
                  | expression LOWER expression
                  | expression HIGHER expression
                  | expression DIVIDE expression'''
    t[0] = (t[2],t[1], t[3])
   
    

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    t[0] = t[1]

def p_expression_function_value_call(t):
    '''expression : NAME LPAREN call_params RPAREN
        | NAME LPAREN RPAREN'''
    if len(t) == 5:
        t[0] = ('function_value_call', t[1], t[3])
    else:
        t[0] = ('function_value_call', t[1], "empty")

def p_error(t):
    print("Syntax error at '%s'" % t.value)

functions_value={}
functions_void={}
functions_scope_stack=[]
names={}

def eval_inst(tree):
    print("evalInst de " + str(tree)) 
    if tree[0] == "bloc":
        eval_inst(tree[1])
        if not (len(functions_scope_stack) > 0 and 'return' in functions_scope_stack[len(functions_scope_stack)-1]):
            eval_inst(tree[2])
    elif tree[0] == "return":
        get_variable_reference("return")["return"] = None if tree[1] == "empty" else eval_expr(tree[1])
    elif tree[0] == "print":
        print(eval_expr(tree[1]))
    elif tree[0] == "print_string":
        print(tree[1])
    elif tree[0] == "assign":
        get_variable_reference(tree[1])[tree[1]]=eval_expr(tree[2])
    elif tree[0] == "if":
        functions_scope_stack.append({})
        if eval_expr(tree[1]):
            eval_inst(tree[2])
        functions_scope_stack.pop()
    elif tree[0] == "while":
        functions_scope_stack.append({})
        while eval_expr(tree[1]):
            eval_inst(tree[2])
        functions_scope_stack.pop()
    elif tree[0] == "for":
        functions_scope_stack.append({})
        eval_inst(tree[1])
        while eval_expr(tree[2]):
            eval_inst(tree[4])
            eval_inst(tree[3])
        functions_scope_stack.pop()
    elif tree[0] == "incr":
        get_variable_reference(tree[1])[tree[1]]+=1
    elif tree[0] == "decr":
        get_variable_reference(tree[1])[tree[1]]-=1
    elif tree[0] == "plus_equals":
        get_variable_reference(tree[1])[tree[1]]+=tree[2]
    elif tree[0] == "minus_equals":
        get_variable_reference(tree[1])[tree[1]]-=tree[2]
    elif tree[0] == "function_void":
        functions_void[tree[1]] = tree
    elif tree[0] == "function_value":
        functions_value[tree[1]] = tree
    elif tree[0] == "function_void_call":
        functions_scope_stack.append({})
        load_function_params(tree, functions_void[tree[1]])
        eval_inst(functions_void[tree[1]][3])
        functions_scope_stack.pop()
    elif tree != "empty":
        eval_expr(tree)

def eval_expr(tree):
    print("evalExpr de " + str(tree))
    if type(tree) == tuple:
        if tree[0] == '+':
            return eval_expr(tree[1]) + eval_expr(tree[2])
        elif tree[0] == '-':
            return eval_expr(tree[1]) - eval_expr(tree[2])
        elif tree[0] == '*':
            return eval_expr(tree[1]) * eval_expr(tree[2])
        elif tree[0] == '/':
            return eval_expr(tree[1]) / eval_expr(tree[2])
        elif tree[0] == '&':
            return eval_expr(tree[1]) and eval_expr(tree[2])
        elif tree[0] == '|':
            return eval_expr(tree[1]) or eval_expr(tree[2])
        elif tree[0] == '>':
            return eval_expr(tree[1]) > eval_expr(tree[2])
        elif tree[0] == '<':
            return eval_expr(tree[1]) < eval_expr(tree[2])
        elif tree[0] == '==':
            return eval_expr(tree[1]) == eval_expr(tree[2])
        elif tree[0] == "function_value_call":
            functions_scope_stack.append({})
            load_function_params(tree, functions_value[tree[1]])
            eval_inst(functions_value[tree[1]][3])
            return_value = get_variable_reference("return")["return"]
            functions_scope_stack.pop()
            return return_value
    elif type(tree) == str:
        return get_variable_reference(tree)[tree]
    elif type(tree) == int:
        return tree


def get_variable_reference(key):
    if key in names or len(functions_scope_stack) == 0:
        return names
    else:
        return functions_scope_stack[len(functions_scope_stack)-1]


def load_function_params(tree, function):
    param_name = function[2]
    print(param_name)
    if param_name != "empty":
        param = tree[2]
        while param and param_name:
            functions_scope_stack[len(functions_scope_stack)-1][param_name[1]] = param[1]
            if len(param) == 2 or len(param_name) == 2:
                break
            param_name = param_name[2]
            param = param[2]

import ply.yacc as yacc
parser = yacc.yacc()

#s='1+2;x=4 if ;x=x+1;'
#s='printString("Hello world");' # print string
#s='for(i=0;i<4;i++;){print(i*i);}'# boucle for et incrementation
#s='max=20;count=0;i=0;j=1;while(count<max)then;count++;print(i);tmp=j+i;i=j;j=tmp;end;' # fibonnacci boucle while
#s='functionVoid voidFunction(a,b){print(a); print(a+b);}voidFunction(1,2);' # void function with params
#s='functionValue valueFunction(a,b){print(1);return a+b;}print(valueFunction(1,2));' # value function with params
#s='functionVoid noParamVoidFunction(){print(10);}noParam();' # void function without params
#s='functionValue noParamValueFunction(){return 10;}print(noParamValueFunction());' # value function without params
#s='functionVoid scoppedVariable(){a=1;}print(a);' # can't access to functions scope variable finish with error
#s='functionVoid globalVariable(){print(a);}a=1;globalVariable();' # void function without params finish with error
s='functionVoid returnStop(){a=1; print(1); return; print(777);}returnStop();' # void function return stops function
#s='functionValue returnStop(){a=1;print(1);return a+1;print(777);}print(returnStop());' # value function return stops function

#with open("1.in") as file: # Use file to refer to the file object

   #s = file.read()

print(parser.parse(s))

