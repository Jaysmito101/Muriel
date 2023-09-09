import os
import sys
import tokenize

INCLUDE_PATHS = ["."]

def print_compiler_error(message, token, moduleName):
    if token is None:
        print("Error: " + message + " in module " + moduleName)
    else:
        print(f"{token.line}")
        print(" " * (token.start[1] - 1) + "^")
        print("Error: " + message + " at line " + str(token.start[0]) + " column " + str(token.start[1]) + " in module " + moduleName)
    sys.exit(1)


def print_help_and_exit(message = None):
    if message:
        print(message)
    
    print("Usage: python muriel.py <input_file> [output_file]")
    sys.exit(1)    

def search_for_include_file(module_info):
    for include_path in INCLUDE_PATHS:
        file = os.path.join(include_path, *module_info) + ".mur"
        if os.path.isfile(file):
            return file
    return None


def extract_block_tokens(tokens, token_index, block_start_char, block_end_char):
    if tokens[token_index].string != block_start_char:
        print_compiler_error(f"expected '{block_start_char}'", tokens[token_index])
    
    block_tokens = []
    block_token_count = 0
    
    while token_index < len(tokens):
        token = tokens[token_index]
        if token.string == block_start_char:
            block_token_count += 1
        elif token.string == block_end_char:
            block_token_count -= 1
            if block_token_count == 0:
                break
        block_tokens.append(token)
        token_index += 1
    
    if token_index >= len(tokens):
        print_compiler_error(f"expected '{block_end_char}'", tokens[token_index - 1])
    
    if block_token_count != 0:
        print_compiler_error(f"mismatched '{block_start_char}' and '{block_end_char}'", tokens[token_index])
    
    return token_index, block_tokens[1:]

class ExternalFunctionAst:
    def __init__(self, parent_ast, name, parameters, return_type):
        self.parent_ast = parent_ast
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
    
    def __str__(self) -> str:
        return f"function(name={self.name}, parameters={self.parameters}, return_type={self.return_type})"

class ExternBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.functions = []

    
    def parse_function(self, tokens, token_index):
        function_name = tokens[token_index].string
        if token_index + 2 >= len(tokens) or tokens[token_index + 1].string != "(":
            print_compiler_error("expected '('", tokens[token_index], self.parent_ast.module_name)
        token_index += 2
        parameter_tokens = []
        while tokens[token_index].string != ")":
            if tokens[token_index].type == tokenize.NAME:
                parameter_tokens.append(tokens[token_index])
            elif tokens[token_index].string == "," or tokens[token_index].type == tokenize.COMMENT or tokens[token_index].type == tokenize.NL or tokens[token_index].type == tokenize.NEWLINE:
                pass
            else:
                print_compiler_error(f"unexpected token '{tokens[token_index].string}'", tokens[token_index], self.parent_ast.module_name)

            token_index += 1
            if token_index >= len(tokens):
                print_compiler_error("expected ')'", tokens[token_index - 1])

        token_index += 1
        if token_index >= len(tokens) or tokens[token_index].string != "->":
            print_compiler_error("expected '->'", tokens[token_index - 1], self.parent_ast.module_name)

        token_index += 1
        if token_index >= len(tokens) or tokens[token_index].type != tokenize.NAME:
            print_compiler_error("expected return type", tokens[token_index - 1], self.parent_ast.module_name)
        return_type = tokens[token_index].string


        token_index += 1
        if token_index >= len(tokens) or (tokens[token_index].type != tokenize.NEWLINE and tokens[token_index].type != tokenize.NL):
            print_compiler_error("expected newline", tokens[token_index - 1], self.parent_ast.module_name)
        
        function = ExternalFunctionAst(self.parent_ast, function_name, parameter_tokens, return_type)
        self.functions.append(function)

        return token_index 
    
    def parse(self, tokens):
        token_index = 0
        while token_index < len(tokens):
            token = tokens[token_index]
            if token.type == tokenize.NAME:
                token_index = self.parse_function(tokens, token_index)
            elif token.type == tokenize.NEWLINE or token.type == tokenize.NL or token.type == tokenize.COMMENT:
                pass
            elif token.type == tokenize.ENDMARKER:
                break
            else:
                print_compiler_error(f"unexpected token '{token.string}'", token, self.parent_ast.module_name)
            token_index += 1

class LoopBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.body = None

    def parse(self, tokens):
        self.body = ScopeBlockAst(self)
        self.body.parse(tokens)

    def __str__(self):
        result = f"loop:\n"
        result += f"{self.body}\n"
        return result        

class IfBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.expression = None
        self.body = None
        self.elif_blocks = []
        self.else_block = None


    def parse(self, if_expression_tokens, if_block_tokens, elif_blocks, else_block_tokens):
        self.expression = if_expression_tokens
        self.body = ScopeBlockAst(self)
        self.body.parse(if_block_tokens)
        
        for elif_expression_tokens, elif_block_tokens in elif_blocks:
            elif_expression = elif_expression_tokens
            elif_body = ScopeBlockAst(self)
            elif_body.parse(elif_block_tokens)
            self.elif_blocks.append((elif_expression, elif_body))
        
        if else_block_tokens:
            self.else_block = ScopeBlockAst(self)
            self.else_block.parse(else_block_tokens)


    def __str__(self):
        result = f"if:\n"
        result += f"{self.body}\n"
        for _, elif_body in self.elif_blocks:
            result += f"elif:\n"
            result += f"{elif_body}\n"
        if self.else_block:
            result += f"else:\n"
            result += f"{self.else_block}\n"
        return result

class WhileBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.expression = None
        self.body = None

    def parse(self, expression_tokens, body_tokens):
        self.body = ScopeBlockAst(self)
        self.body.parse(body_tokens)
        self.expression = expression_tokens

    def __str__(self):
        result = f"while:\n"
        result += f"{self.body}\n"
        return result

class SwitchBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.variable_name = None
        self.cases = []
        self.default_case = None
        self.vname = None
    
    def parse(self, vname, tokens):
        self.vname = vname
        token_index = 0
        tokens = tokens[1:]
        while True:
            if token_index >= len(tokens):
                break
            while tokens[token_index].type == tokenize.NL or tokens[token_index].type == tokenize.NEWLINE or tokens[token_index].type == tokenize.COMMENT:
                token_index += 1
                if token_index >= len(tokens):
                    break
            if token_index >= len(tokens) or tokens[token_index].string == "}":
                break            
            expr_tokens = []
            while tokens[token_index].string != ":":
                if tokens[token_index].type == tokenize.NL or tokens[token_index].type == tokenize.NEWLINE:
                    print_compiler_error("expected ':'", tokens[token_index - 1], self.module_name)
                if tokens[token_index].type == tokenize.NAME and tokens[token_index].string != "default":
                    print_compiler_error("expected case value to be a constant or constant expression", tokens[token_index], self.module_name)
                if tokens[token_index].string == "{":
                    print_compiler_error("expected ':'", tokens[token_index], self.module_name)                
                expr_tokens.append(tokens[token_index])
                token_index += 1
                if token_index >= len(tokens):
                    print_compiler_error("expected ':'", tokens[token_index - 1], self.module_name)
            if len(expr_tokens) == 0:
                print_compiler_error("expected case value", tokens[token_index], self.module_name)
            if token_index + 1 >= len(tokens) or tokens[token_index + 1].string != "{":
                print_compiler_error("expected '{'", tokens[token_index], self.module_name)
            token_index += 1
            token_index, block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
            expr_block = ExpressionAst(self)
            expr_block.parse(expr_tokens)
            body_block = ScopeBlockAst(self)
            body_block.parse(block_tokens)
            self.cases.append((expr_block, body_block))           
            token_index += 1

            

    def __str__(self):
        result = f"switch({self.vname}):\n"
        result += f"num_cases: {len(self.cases)}\n"
        return result
    
class ExpressionAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.expression = None

    def parse(self, tokens):
        pass

    def __str__(self):
        result = f"expression:\n"
        return result

class ScopeBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.statements = []
    
    def parse_if_statement(self, tokens, token_index):
        token_index += 1
        if_expression_tokens = []
        while tokens[token_index].string != "{":
            if_expression_tokens.append(tokens[token_index])
            token_index += 1
            if token_index >= len(tokens):
                print_compiler_error("expected '{'", tokens[token_index - 1], self.parent_ast.module_name)
        token_index, if_block_tokens = extract_block_tokens(tokens, token_index, '{', '}')

        elif_blocks = []
        while token_index + 1 < len(tokens) and tokens[token_index + 1].string == "elif":
            token_index += 2
            elif_expression_tokens = []
            while tokens[token_index].string != "{":
                elif_expression_tokens.append(tokens[token_index])
                token_index += 1
                if token_index >= len(tokens):
                    print_compiler_error("expected '{'", tokens[token_index - 1], self.parent_ast.module_name)
            token_index, elif_block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
            elif_blocks.append((elif_expression_tokens, elif_block_tokens))          
                

        else_block_tokens = None
        if token_index + 1 < len(tokens) and tokens[token_index + 1].string == "else":
            if token_index + 2 >= len(tokens) or tokens[token_index + 2].string != "{":
                print_compiler_error("expected '{'", tokens[token_index + 1], self.parent_ast.module_name)
            token_index += 2                
            token_index, else_block_tokens = extract_block_tokens(tokens, token_index, '{', '}')

        # self.statements.append(("if", if_expression_tokens, if_block_tokens, elif_blocks, else_block_tokens))
        if_block = IfBlockAst(self)
        if_block.parse(if_expression_tokens, if_block_tokens, elif_blocks, else_block_tokens)
        self.statements.append(if_block)
        return token_index

    def parse_while_statement(self, tokens, token_index):
        token_index += 1
        while_expression_tokens = []
        while tokens[token_index].string != "{":
            while_expression_tokens.append(tokens[token_index])
            token_index += 1
            if token_index >= len(tokens):
                print_compiler_error("expected '{'", tokens[token_index - 1], self.parent_ast.module_name)
        token_index, while_block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
        while_block = WhileBlockAst(self)
        while_block.parse(while_expression_tokens, while_block_tokens)
        self.statements.append(while_block)
        return token_index
        
    def parse_loop_statement(self, tokens, token_index):
        if token_index + 1 > len(tokens) or tokens[token_index + 1].string != "{":
            print_compiler_error("expected '{'", tokens[token_index], self.parent_ast.module_name)
        token_index += 1
        token_index, loop_block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
        loop_block = LoopBlockAst(self)
        loop_block.parse(loop_block_tokens)
        self.statements.append(loop_block)
        return token_index

    def parse_switch_statement(self, tokens, token_index):
        if token_index + 1 >= len(tokens) or tokens[token_index + 1].type != tokenize.NAME:
            print_compiler_error("expected switch variable", tokens[token_index], self.parent_ast.module_name)

        if token_index + 2 >= len(tokens) or tokens[token_index + 2].string != "{":
            print_compiler_error("expected '{'", tokens[token_index], self.parent_ast.module_name)
        token_index += 2

        variable_name = tokens[token_index - 2].string
        token_index, switch_block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
        switch_block = SwitchBlockAst(self)
        switch_block.parse(variable_name, switch_block_tokens)
        self.statements.append(switch_block)
        return token_index

    def parse(self, tokens):
        token_index = 0
        while token_index < len(tokens):
            token = tokens[token_index]
            if token.type == tokenize.NEWLINE or token.type == tokenize.NL or token.type == tokenize.COMMENT:
                pass
            elif token.type == tokenize.ENDMARKER:
                break
            elif token.type == tokenize.NAME:
                if token.string == "if":
                    token_index = self.parse_if_statement(tokens, token_index)
                elif token.string == "while":
                    token_index = self.parse_while_statement(tokens, token_index)
                elif token.string == "loop":
                    token_index = self.parse_loop_statement(tokens, token_index)
                elif token.string == "switch":
                    token_index = self.parse_switch_statement(tokens, token_index)
                else:
                    expression_tokens = []
                    while tokens[token_index].type != tokenize.NEWLINE and tokens[token_index].type != tokenize.NL:
                        expression_tokens.append(tokens[token_index])
                        token_index += 1
                        if token_index >= len(tokens):
                            print_compiler_error("expected newline", tokens[token_index - 1], self.parent_ast.module_name)
                    token_index -= 1
                    expression = ExpressionAst(self)
                    expression.parse(expression_tokens)
                    self.statements.append(expression)
            else:
                print_compiler_error(f"unexpected token '{token.string}'", token, self.parent_ast.module_name)
            token_index += 1

    def __str__(self):
        result = f"scope:\n"
        for statement in self.statements:
            result += f"{statement}\n"
        return result

class FunctionBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.name = None
        self.parameters = []
        self.body = None


    def parse(self, name, parameters, tokens):
        self.name = name
        self.parameters = parameters
        self.body = ScopeBlockAst(self)
        self.body.parse(tokens)

    
    def __str__(self) -> str:
        result = f"function({self.name}):\n"
        result += f"parameters: {self.parameters}\n"
        result += f"body:\n"
        result += f"{self.body}\n"
        return result

class NamespaceBlockAst:
    def __init__(self, parent_ast):
        self.parent_ast = parent_ast
        self.module_name = parent_ast.module_name
        self.functions = {}
        self.name = None

    def parse_function(self, tokens, token_index):
        function_name = tokens[token_index].string

        if token_index + 2 >= len(tokens) or tokens[token_index + 1].string != "(":            
            print_compiler_error("expected '('", tokens[token_index], self.parent_ast.module_name)
        token_index += 2
    
        parameter_tokens = []
        while tokens[token_index].string != ")":
            if tokens[token_index].type == tokenize.NAME:
                parameter_tokens.append(tokens[token_index].string)
            elif tokens[token_index].string == "," or tokens[token_index].type == tokenize.COMMENT or tokens[token_index].type == tokenize.NL or tokens[token_index].type == tokenize.NEWLINE:
                pass
            else:
                print_compiler_error(f"unexpected token '{tokens[token_index].string}'", tokens[token_index], self.parent_ast.module_name)

            token_index += 1
            if token_index >= len(tokens):
                print_compiler_error("expected ')'", tokens[token_index - 1])
            
        token_index += 1

        while token_index < len(tokens) and tokens[token_index].string != "{":
            token_index += 1
        
        if token_index >= len(tokens) or tokens[token_index].string != "{":
            print_compiler_error("expected '{'", tokens[token_index - 1], self.parent_ast.module_name)
        
        token_index, block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
        functionBlock = FunctionBlockAst(self)
        functionBlock.parse(function_name, parameter_tokens, block_tokens)
        self.functions[function_name] = functionBlock
        return token_index
        
    def parse(self, namespace_name, tokens):
        self.name = namespace_name

        token_index = 0
        while token_index < len(tokens):
            token = tokens[token_index]
            if token.type == tokenize.NAME:
                token_index = self.parse_function(tokens, token_index)
            elif token.type == tokenize.NEWLINE or token.type == tokenize.NL:
                pass
            else:
                print_compiler_error(f"unexpected token '{token.string}'", token, self.parent_ast.module_name)
            token_index += 1
    
    def __str__(self) -> str:
        result = f"namespace({self.name}):\n"
        for function_name in self.functions:
            result += f"{function_name}:\n"
            result += f"{self.functions[function_name]}\n"
        return result


class MurielAst:
    def __init__(self, module_name, modules_added = []):
        self.modules_added = modules_added
        self.module_name = module_name
        self.modules = {}
        self.alias_map = {}
        self.external_functions = {}
        self.namespaces = {}

    def parse_include(self, tokens, token_index):
        # include (core.stdio) as stdio
        if token_index + 2 >= len(tokens):
            print_compiler_error("expected module name", tokens[token_index - 1], self.module_name)
        
        if tokens[token_index + 1].string != "(":
            print_compiler_error("expected '('", tokens[token_index + 1], self.module_name)
        
        if tokens[token_index + 2].type != tokenize.NAME:
            print_compiler_error("expected module name after '('", tokens[token_index + 2], self.module_name)
        
        token_index += 2
        module_tokens = []
        while tokens[token_index].string != ")":
            if tokens[token_index].type == tokenize.NAME:
                module_tokens.append(tokens[token_index].string)
            elif tokens[token_index].string == ".":
                pass
            else:
                print_compiler_error(f"unexpected token '{tokens[token_index].string}'", tokens[token_index], self.module_name)
            token_index += 1
            if token_index >= len(tokens):
                print_compiler_error("expected ')'", tokens[token_index - 1])

        module_alias = None
        if token_index + 1 < len(tokens) and tokens[token_index + 1].string == "as":
            if token_index + 2 >= len(tokens):
                print_compiler_error("expected module alias", tokens[token_index + 1], self.module_name)
            if tokens[token_index + 2].type != tokenize.NAME:
                print_compiler_error("expected module alias", tokens[token_index + 2], self.module_name)
            module_alias = tokens[token_index + 2].string
            token_index += 3

        if token_index >= len(tokens) or tokens[token_index].type != tokenize.NEWLINE:
            print_compiler_error("expected newline", tokens[token_index - 1], self.module_name)

        return token_index, module_tokens, module_alias            


    def process_include(self, module_info, module_alias):
        file = search_for_include_file(module_info)
        if not file:
            print_compiler_error(f"could not find module '{'.'.join(module_info)}'", None, self.module_name)
        
        tokens = []
        with open(file, 'rb') as f:
            tokens = list(tokenize.tokenize(f.readline))
        
        module_name = os.path.splitext(os.path.basename(file))[0]
        if module_alias:
            self.alias_map[module_alias] = module_name
        
        if module_name in self.modules_added:
            return

        self.modules_added.append(module_name)

        sub_ast = MurielAst(module_name, self.modules_added)
        sub_ast.parse(tokens[1:])

        self.modules[".".join(module_info)] = sub_ast

        sub_ast_modules = sub_ast.modules
        for sub_ast_module_name in sub_ast_modules:
            self.modules[sub_ast_module_name] = sub_ast_modules[sub_ast_module_name]

        # sub_ast_alias_map = sub_ast.alias_map
        # for sub_ast_alias in sub_ast_alias_map:
        #     self.alias_map[sub_ast_alias] = sub_ast_alias_map[sub_ast_alias]

    def parse_extern_block(self, tokens):       
        externBlock = ExternBlockAst(self)
        externBlock.parse(tokens)
        for function in externBlock.functions:
            self.external_functions[function.name] = function

    def parse_namespace_block(self, namespace_name, tokens):
        if namespace_name in self.namespaces:
            print_compiler_error(f"namespace '{namespace_name}' already defined", None, self.module_name)
        namespaceBlock = NamespaceBlockAst(self)
        namespaceBlock.parse(namespace_name, tokens)
        self.namespaces[namespace_name] = namespaceBlock

    def parse(self, tokens):
        token_index = 0
        while token_index < len(tokens):        
            token = tokens[token_index]
            if token.type == tokenize.COMMENT:
                pass
            elif token.type == tokenize.NAME:
                if token.string == "include":
                    token_index, module_info, mopdule_alias = self.parse_include(tokens, token_index)
                    self.process_include(module_info, mopdule_alias)
                elif token.string == "extern":
                    if token_index + 2 >= len(tokens) or tokens[token_index + 1].string != '{':
                        print_compiler_error("expected a block after after extern", tokens[token_index], self.module_name)
                    token_index += 1
                    token_index, block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
                    self.parse_extern_block(block_tokens)
                else:
                    namespace_name = token.string
                    if token_index + 1 >= len(tokens) or tokens[token_index + 1].string != '{':
                        print_compiler_error("expected a block after namespace", tokens[token_index], self.module_name)
                    token_index += 1
                    token_index, block_tokens = extract_block_tokens(tokens, token_index, '{', '}')
                    self.parse_namespace_block(namespace_name, block_tokens)
            elif token.type == tokenize.NEWLINE or token.type == tokenize.NL:
                pass
            elif token.type == tokenize.ENDMARKER:
                break
            else:
                print_compiler_error(f"unexpected token '{token.string}'", token, self.module_name)          
            token_index += 1
        
        if "global" not in self.namespaces:
            print_compiler_error("expected namespace 'global'", None, self.module_name)


    def __str__(self) -> str:
        result = f"module({self.module_name}):\n"

        if len(self.modules) > 0:
            result += "includes:\n"
            for module_name in self.modules:
                result += f"{module_name}\n"

        if len(self.external_functions) > 0:
            result += "external functions:\n"
            for function_name in self.external_functions:
                result += f"{function_name}\n"
            
        if len(self.namespaces) > 0:
            result += "namespaces:\n"
            for namespace_name in self.namespaces:
                result += f"{namespace_name}\n"

        return result
        

                    
                    

        
    

def main():
    if len(sys.argv) < 2:
        print_help_and_exit("Error: no input file specified")

    inputFile = sys.argv[1]

    if not os.path.isfile(inputFile):
        print_help_and_exit("Error: input file does not exist")

    outputFile = inputFile + ".out.c"
    if len(sys.argv) > 2:
        outputFile = sys.argv[2]
    
    tokens = []
    with open(inputFile, 'rb') as f:
        tokens = list(tokenize.tokenize(f.readline))

    with open(outputFile, 'w') as f:
        for token in tokens:
            f.write(str(token))
            f.write('\n')

    file_name_without_extension = os.path.splitext(os.path.basename(inputFile))[0]
    ast = MurielAst(file_name_without_extension)
    ast.parse(tokens[1:])


    #print(ast)
    for namespace_name in ast.namespaces:
        print(namespace_name)
        print(ast.namespaces[namespace_name])
        print("-----------------------------")

    
    


if __name__ == '__main__':
    main()