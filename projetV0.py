from genereTreeGraphviz2 import printTreeGraph
import sys,ctypes,copy

reserved = {
   'if' : 'IF',
   'else' : 'ELSE',
   'print' : 'PRINT',
   'printString' : 'PRINT_STRING',
   'while' : 'WHILE',
   'for' : 'FOR',
   'functionValue' : "FONCTION_VALUE",
   'functionVoid' : "FONCTION_VOID",
   'return' : 'RETURN',
   'length' : 'LENGTH',
   'class' : 'CLASS',
   'new' : 'NEW',
   'extends' : 'EXTENDS'
   }

tokens = [
    'STRING','NAME','NUMBER', 'COMMENT','MULTILINE_COMMENT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 
    'AND', 'OR', 'EQUAL', 'LOWER','HIGHER', 'LOWER_OR_EQUAL', 'HIGHER_OR_EQUAL',
    'LPAREN','RPAREN', 'LBRACKET','RBRACKET','LBRACKETS','RBRACKETS',
    'COLON', 'COMMA','DOT'
    ]+list(reserved.values())

# Tokens
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t

def t_STRING(t):
    r'[\'"][^\'"\n]*[\'"]'
    t.type = reserved.get(t.value,'STRING')    # Check for reserved words
    t.value = t.value[1:-1]
    return t

def t_COMMENT(t):
    r'(//.*)'
    t.type = reserved.get(t.value,'COMMENT')    # Check for reserved words
    t.value = t.value[2:]
    return t

def t_MULTILINE_COMMENT(t):
    r'(/\*(.|\n)*?\*/)'
    t.type = reserved.get(t.value,'MULTILINE_COMMENT')    # Check for reserved words
    t.value = t.value[2:-2]
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
t_RBRACKETS  = r'\]'
t_LBRACKETS  = r'\['
t_COLON = r';'
t_COMMA = r','
t_AND  = r'\&'
t_OR  = r'\|'
t_EQUAL  = r'=='
t_LOWER  = r'\<'
t_LOWER_OR_EQUAL  = r'\<='
t_HIGHER  = r'\>'
t_HIGHER_OR_EQUAL  = r'\>='
t_DOT    = r'.'

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
    ('left','AND', 'OR', 'EQUAL', 'LOWER','HIGHER', 'LOWER_OR_EQUAL', 'HIGHER_OR_EQUAL'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

 

def p_start(t):
    ''' start : linst'''
    t[0] = ('start',t[1])
    print(t[0])
    printTreeGraph(t[0])
    eval_inst(t[1])
    
def p_line(t):
    '''linst : linst inst 
            | inst '''
    if len(t)== 3 :
        t[0] = ('bloc',t[1], t[2])
    else:
        t[0] = ('bloc',t[1], 'empty')

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
    '''inst : FONCTION_VALUE NAME LPAREN params RPAREN LBRACKET linst RBRACKET
        | FONCTION_VALUE NAME LPAREN RPAREN LBRACKET linst RBRACKET'''
    if len(t) == 9:
        t[0] = ('function_value', t[2], t[4], t[7])
    else:
        t[0] = ('function_value', t[2], "empty", t[6])


def p_statement_function_void_definition(t):
    '''inst : FONCTION_VOID NAME LPAREN params RPAREN LBRACKET linst RBRACKET
        | FONCTION_VOID NAME LPAREN RPAREN LBRACKET linst RBRACKET'''
    if len(t) == 9:
        t[0] = ('function_void', t[2], t[4], t[7])
    else:
        t[0] = ('function_void', t[2], "empty", t[6])

def p_statement_return_value(t):
    '''inst : RETURN expression COLON'''
    t[0] = ('return', t[2])

def p_statement_return_void(t):
    '''inst : RETURN COLON'''
    t[0] = ('return', 'empty')

def p_statement_while(t):
    'inst : WHILE LPAREN expression RPAREN LBRACKET linst RBRACKET'
    t[0] = ('while', t[3], t[6])

def p_statement_for(t):
    'inst : FOR LPAREN inst expression COLON inst RPAREN LBRACKET linst RBRACKET'
    t[0] = ('for', t[3], t[4], t[6], t[9])

def p_statement_assign(t):
    'inst : NAME EQUALS expression COLON'
    t[0] = ('assign', t[1], t[3])

def p_statement_assign_ptr(t):
    'inst : TIMES NAME EQUALS expression COLON'
    t[0] = ('assign_ptr', t[2], t[4])

def p_statement_print(t):
    'inst : PRINT LPAREN call_params RPAREN COLON'
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

def p_conditional(t):
    'inst : conditional_if'
    t[0] = t[1]

def p_statement_if(t):
    '''conditional_if : IF LPAREN expression RPAREN LBRACKET linst RBRACKET 
        | IF LPAREN expression RPAREN LBRACKET linst RBRACKET conditional_else'''
    if len(t) == 8:
        t[0] = ('if', t[3], t[6], 'empty')
    else:
        t[0] = ('if', t[3], t[6], t[8])

def p_statement_else(t):
    '''conditional_else : ELSE conditional_if 
        | ELSE LBRACKET linst RBRACKET'''
    if len(t) == 3:
        t[0] = t[2]
    else:
        t[0] = (t[3])

def p_statement_class(t):
    '''inst : CLASS NAME LBRACKET linst RBRACKET
        | CLASS NAME EXTENDS NAME LBRACKET linst RBRACKET'''
    if len(t) == 6:
        t[0] = ('class', t[2], 'empty', t[4])
    else:
        t[0] = ('class',t[2],t[4], t[6])

def p_statement_object_instantiation(t):
    '''inst : NAME EQUALS NEW NAME LPAREN RPAREN COLON
            | NAME EQUALS NEW NAME LPAREN params RPAREN COLON'''
    if len(t) == 8:
        t[0] = ('object_instantiate', t[1], t[4], 'empty')
    else:
        t[0] = ('object_instantiate', t[1], t[4], t[6])

def p_statement_object_call(t):
    'inst : NAME DOT inst'
    t[0] = ('class_inst_call',t[1], t[3])

def p_statement_comment(t):
    '''inst : COMMENT
        | MULTILINE_COMMENT'''
    t[0] = ('comment', t[1])

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression OR expression
                  | expression AND expression
                  | expression EQUAL expression
                  | expression LOWER expression
                  | expression LOWER_OR_EQUAL expression
                  | expression HIGHER expression
                  | expression HIGHER_OR_EQUAL expression
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

def p_expression_var_addr(t):
    'expression : AND NAME'
    t[0] = ('var_addr', t[2])

def p_expression_var_ptr(t):
    'expression : TIMES NAME'
    t[0] = ('var_ptr', t[2])

def p_expression_function_value_call(t):
    '''expression : NAME LPAREN call_params RPAREN
        | NAME LPAREN RPAREN'''
    if len(t) == 5:
        t[0] = ('function_value_call', t[1], t[3])
    else:
        t[0] = ('function_value_call', t[1], "empty")

def p_expression_tab_init(t):
    '''expression : LBRACKETS call_params RBRACKETS'''
    t[0] = ('array', t[2])

def p_expression_tab_element_access(t):
    'expression : NAME LBRACKETS expression RBRACKETS'
    t[0] = ('array_access', t[1], t[3])

def p_expression_tab_length(t):
    'expression : LENGTH LPAREN NAME RPAREN'
    t[0] = ('array_length', t[3])

def p_expression_object_call(t):
    'expression : NAME DOT expression'
    t[0] = ('class_expr_call',t[1], t[3])

def p_error(t):
    print("Syntax error at '%s'" % t.value)


classes={}
functions_value={}
functions_void={}
functions_scope_stack=[]
names={}
doc_string=open("docString.txt",'w')

def eval_inst(tree, instance=None):
    print("evalInst de " + str(tree)) 
    if tree[0] == "bloc":
        eval_inst(tree[1], instance)
        if not (len(functions_scope_stack) > 0 and 'return' in functions_scope_stack[len(functions_scope_stack)-1]):
            eval_inst(tree[2], instance)
    elif tree[0] == "return":
        get_variable_reference("return")["return"] = None if tree[1] == "empty" else eval_expr(tree[1], instance)
    elif tree[0] == "print":
        print(' '.join(str(x) for x in get_params_to_array(tree[1],instance)))
    elif tree[0] == "print_string":
        print(tree[1])
    elif tree[0] == 'assign_ptr':
        mutate(ctypes.cast(copy.deepcopy(get_variable_reference(tree[1])[tree[1]]), ctypes.py_object).value, eval_expr(tree[2]))
    elif tree[0] == "assign":
        get_variable_reference(tree[1], instance)[tree[1]]=eval_expr(tree[2], instance)
    elif tree[0] == "if":
        if eval_expr(tree[1], instance):
            eval_inst(tree[2], instance)
        else:
            eval_inst(tree[3], instance)
    elif tree[0] == "while":
        while eval_expr(tree[1], instance):
            eval_inst(tree[2], instance)
    elif tree[0] == "for":
        eval_inst(tree[1])
        while eval_expr(tree[2], instance):
            eval_inst(tree[4], instance)
            eval_inst(tree[3], instance)
    elif tree[0] == "incr":
        get_variable_reference(tree[1], instance)[tree[1]]+=1
    elif tree[0] == "decr":
        get_variable_reference(tree[1], instance)[tree[1]]-=1
    elif tree[0] == "plus_equals":
        get_variable_reference(tree[1], instance)[tree[1]]+=eval_expr(tree[2], instance)
    elif tree[0] == "minus_equals":
        get_variable_reference(tree[1], instance)[tree[1]]-=eval_expr(tree[2], instance)
    elif tree[0] == "function_void":
        if instance == None:
            functions_void[tree[1]] = tree
        else:
            instance["functions_void"][tree[1]] = tree
    elif tree[0] == "function_value":
        if instance == None:
            functions_value[tree[1]] = tree
        else:
            instance["functions_value"][tree[1]] = tree
    elif tree[0] == "function_void_call":
        load_function_params(tree, get_void_function_reference(tree[1], instance), instance)
        eval_inst(get_void_function_reference(tree[1], instance)[3], instance)
        functions_scope_stack.pop()
    elif tree[0] == "array":
        get_variable_reference(tree[1], instance)[tree[1]]=eval_expr(tree[2])
    elif tree[0] == "class":
        classes[tree[1]] = tree
    elif tree[0] == "object_instantiate":
        get_variable_reference(tree[1], instance)[tree[1]]=instantiate_object(tree[2])
    elif tree[0] == "class_inst_call":
        eval_inst(tree[2], get_variable_reference(tree[1], instance)[tree[1]])
    elif tree != "empty":
        eval_expr(tree, instance)


def instantiate_object(class_name):
    clas=classes[class_name]
    obj={}
    obj["functions_value"]={}
    obj["functions_void"]={}
    if clas[2] != "empty":
        obj["super"]=instantiate_object(clas[2])
    eval_inst(clas[3], obj)
    return obj

def eval_expr(tree, instance = None):
    print("evalExpr de " + str(tree))
    if type(tree) == tuple:
        if tree[0] == '+':
            return eval_expr(tree[1], instance) + eval_expr(tree[2], instance)
        elif tree[0] == '-':
            return eval_expr(tree[1], instance) - eval_expr(tree[2], instance)
        elif tree[0] == '*':
            return eval_expr(tree[1], instance) * eval_expr(tree[2], instance)
        elif tree[0] == '/':
            return eval_expr(tree[1]) / eval_expr(tree[2], instance)
        elif tree[0] == '&':
            return eval_expr(tree[1], instance) and eval_expr(tree[2], instance)
        elif tree[0] == '|':
            return eval_expr(tree[1], instance) or eval_expr(tree[2], instance)
        elif tree[0] == '>':
            return eval_expr(tree[1], instance) > eval_expr(tree[2], instance)
        elif tree[0] == '<':
            return eval_expr(tree[1], instance) < eval_expr(tree[2], instance)
        elif tree[0] == '>=':
            return eval_expr(tree[1], instance) >= eval_expr(tree[2], instance)
        elif tree[0] == '<=':
            return eval_expr(tree[1], instance) <= eval_expr(tree[2], instance)
        elif tree[0] == '==':
            return eval_expr(tree[1], instance) == eval_expr(tree[2], instance)
        elif tree[0] == "function_value_call":
            load_function_params(tree, get_value_function_reference(tree[1], instance), instance)
            eval_inst(get_value_function_reference(tree[1], instance)[3], instance)
            return_value = get_variable_reference("return")["return"]
            functions_scope_stack.pop()
            return return_value
        elif tree[0] == 'array':
            return parse_array(tree[1])
        elif tree[0] == 'array_access':
            return get_variable_reference(tree[1], instance)[tree[1]][tree[2]]
        elif tree[0] == 'array_length':
            return len(get_variable_reference(tree[1], instance)[tree[1]])
        elif tree[0] == 'class_expr_call':
            return eval_expr(tree[2], get_variable_reference(tree[1])[tree[1]])
        elif tree[0] == 'var_addr':
            return id(get_variable_reference(tree[1])[tree[1]])
        elif tree[0] == 'var_ptr':
            return ctypes.cast(get_variable_reference(tree[1])[tree[1]], ctypes.py_object).value
        elif tree[0] == 'comment':
            doc_string.write(tree[1]+'\n\n')
    elif type(tree) == str:
        return get_variable_reference(tree, instance)[tree]
    elif type(tree) == int:
        return tree

def get_void_function_reference(key, instance=None):
    instance_fn=get_void_function_from_instance(key, instance)
    if instance_fn != None:
        return instance_fn
    else:
        return functions_void[key]

def get_value_function_reference(key, instance=None):
    instance_fn=get_value_function_from_instance(key, instance)
    if instance_fn != None:
        return instance_fn
    else:
        return functions_value[key]

def get_void_function_from_instance(key, instance):
    while instance != None:
        if key in instance["functions_void"]:
            return instance["functions_void"][key]
        instance = instance["super"] if super in instance else None

def get_value_function_from_instance(key, instance):
    while instance != None:
        if key in instance["functions_value"]:
            return instance["functions_value"][key]
        instance = instance["super"] if "super" in instance else None

def get_variable_reference(key, instance=None):
    if key in names or len(functions_scope_stack) == 0 and instance == None:
        return names
    elif len(functions_scope_stack) != 0 and key in functions_scope_stack[len(functions_scope_stack)-1] or instance == None:
        return functions_scope_stack[len(functions_scope_stack)-1]
    elif get_super_variable_reference(key,instance) != None:
        return get_super_variable_reference(key, instance)
    else:
        return instance

def get_super_variable_reference(key,instance):
    while instance != None:
        if key in instance:
            return instance
        instance = instance["super"] if "super" in instance else None

def get_params_to_array(params, instance):
    tab=[]
    while params != None:
        tab.append(eval_expr(params[1],instance))
        params = params[2] if len(params) == 3 else None
    return tab

def load_function_params(tree, function, instance=None):
    params={}
    param_name = function[2]
    if param_name != "empty":
        param = tree[2]
        while param and param_name:
            params[param_name[1]] = eval_expr(param[1], instance)
            if len(param) == 2 or len(param_name) == 2:
                break
            param_name = param_name[2]
            param = param[2]
    functions_scope_stack.append(params)

def parse_array(tree, tab=[]):
    tab.append(tree[1])
    if len(tree) == 3:
        parse_array(tree[2], tab)
    return tab

def mutate(obj, new_obj):
    if sys.getsizeof(obj) != sys.getsizeof(new_obj):
        raise ValueError('objects must have same size')
    mem = (ctypes.c_byte * sys.getsizeof(obj)).from_address(id(obj))
    new_mem = (ctypes.c_byte * sys.getsizeof(new_obj)).from_address(id(new_obj))
    for i in range(len(mem)):
        mem[i] = new_mem[i]

import ply.yacc as yacc
parser = yacc.yacc()

#s='x=1;print(x);'
#s='printString("Hello world");' # print string
#s='for(i=0;i<4;i++;){print(i*i);}'# boucle for et incrementation
#s='max=20;count=0;i=0;j=1;while(count<max){count++;print(i);tmp=j+i;i=j;j=tmp;}' # fibonnacci boucle while
#s='functionVoid voidFunction(a,b){print(a); print(a+b);}voidFunction(1,2);' # void function with params
#s='functionValue valueFunction(a,b){return a+b;}print(valueFunction(1,2));' # value function with params
#s='functionVoid noParamVoidFunction(){print(10);}noParamVoidFunction();' # void function without params
#s='functionValue noParamValueFunction(){return 10;}print(noParamValueFunction());' # value function without params
#s='functionVoid scoppedVariable(){a=1;}scoppedVariable();print(a);' # can't access to functions scope variable finish with error
#s='functionVoid globalVariable(){print(a);}a=1;globalVariable();' # void function without params finish with error
#s='functionVoid returnStop(){a=1; print(1); return; print(777);}returnStop();' # void function return stops function
#s='functionValue returnStop(){a=1;print(1);return a+1;print(777);}print(returnStop());' # value function return stops function
#s='functionValue fibonacci(n){if(n>=2){return fibonacci(n-1) + fibonacci(n - 2);} if((n == 0) | (n == 1)){return 1;}}print(fibonacci(10));' # Recursive fibonacci function
#s='x=0;if(x==1){printString("should not display");}else{printString("should be displayed");}' # Use of else block
#s='x=0; if(x>=1){printString("should not display");}else if(x<=0){printString("should be displayed");}else{printString("should not display");}' # use of else if block
#s='x=1;x+=5;print(x);'
#s='x=1;x-=5;print(x);'

# Newly added code
#s='x=[5,6,7,8,9];print(x);'# Init array and print content
#s='x=[5,6,7,8,9];print(x[1]);'# Init array and print element accessed by index
#s='x=[5,6,7,8,9];print(length(x));'#Get size of an array

#s='class Car { kilometer=0; functionValue getKilometer(){ return kilometer; } functionVoid setKilometer(value){ kilometer = value; } functionVoid move(){ setKilometer(kilometer+1); } } car= new Car(); car.move(); print(car.kilometer); car.setKilometer(5);print(car.getKilometer()); print(car);' # Define class instantiate it and call inner functions and properties
#s='''class Animal { x=1; functionValue getX(){ return x; } }
# class Dog extends Animal { functionVoid setX(value){super.x=value;} functionVoid makeNoise() { printString("Waf"); } }
# class Cat extends Animal { functionVoid makeNoise() { printString("Miaou"); } }
# cat= new Cat(); dog = new Dog(); dog.makeNoise(); cat.makeNoise(); print(dog.getX()); dog.setX(10); print(dog.getX()); print(cat.getX());''' 
# Create mother class animal which is implemented by two subclasses dog and cat both make prints different string they doesn't share the same mother instance and dog can edit super's property

#s="x=1;print(x,2,x+2);"# Print with multiple parameters

#s='functionVoid increment(ptr){ print(ptr);print(*ptr);*ptr=*ptr+1; } x=6;print(&x); increment(&x); print(x);'# Make use of pointers to increment the value in a function and display the address of the variable in memory

s='''//print a string print(1);
printString("AAAAAAAAAAAA");
/*test other comment format print(1);*/''' # the code inside comments is ignored and comments are written into a file called "docString.text"

#with open("1.in") as file: # Use file to refer to the file object

   #s = file.read()

parser.parse(s)
doc_string.close()