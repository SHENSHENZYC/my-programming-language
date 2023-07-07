from string_with_arrows import string_with_arrows


############################################
# CONSTANTS
############################################

NUM_CHARS = '0123456789.'


############################################
# ERROR
############################################

class Error:
    def __init__(self, start_pos, end_pos, error_name, error_message):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.error_name = error_name
        self.error_message = error_message

    def as_string(self):
        res =  f'{self.error_name}: {self.error_message}\n' \
            + f'File {self.start_pos.file_name}, line {self.start_pos.ln + 1}:\n\n' \
            + string_with_arrows(self.start_pos.file_text, self.start_pos, self.end_pos)
        
        return res


class IllegalCharError(Error):
    def __init__(self, start_pos, end_pos, error_message):
        super(IllegalCharError, self).__init__(start_pos, end_pos, 'IllegalCharacterError', error_message)
        

class InvalidSyntaxError(Error):
    def __init__(self, start_pos, end_pos, error_message):
        super(InvalidSyntaxError, self).__init__(start_pos, end_pos, 'InvalidSyntaxError', error_message)
        

class RuntimeError_(Error):
    def __init__(self, start_pos, end_pos, error_message, context):
        super(RuntimeError_, self).__init__(start_pos, end_pos, 'RuntimeError', error_message)
        self.context = context

    def generate_traceback(self):
        """Trace back hierarchically to where the error happens in the main program."""
        result = ''
        pos = self.start_pos
        context = self.context
        
        while context:
            result = f'    File {pos.file_name}, line {pos.ln + 1}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        
        return 'Traceback (most recent call last):\n' + result

    def as_string(self):
        res = self.generate_traceback()
        res +=  f'{self.error_name}: {self.error_message}\n' \
            + string_with_arrows(self.start_pos.file_text, self.start_pos, self.end_pos)
        
        return res


############################################
# POSITION
############################################

class Position:
    def __init__(self, idx, ln, col, file_name, file_text):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.file_name = file_name
        self.file_text = file_text
    
    def advance(self, curr_char=None):
        self.idx += 1
        self.col += 1
        
        # check if we are switching to a new line in the script
        if curr_char == '\n':
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.file_name, self.file_text)
        

############################################
# TOKEN
############################################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'


class Token:
    def __init__ (self, type_, value=None, start_pos=None, end_pos=None):
        self.type = type_
        self.value = value
        
        if start_pos:
            self.start_pos = start_pos.copy()
            
            # case: start_pos given but end_pos not given
            self.end_pos = start_pos.copy()
            self.end_pos.advance()
            
        if end_pos:
            self.end_pos = end_pos.copy()
        
    def __repr__(self):
        if self.value:
            return f'{self.type}: {self.value}'
        else:
            return f'{self.type}'
        

class Lexer:
    def __init__ (self, file_name, text):
        self.file_name = file_name
        self.text = text
        
        # set up cursor to track position and character in the text
        self.curr_pos = Position(-1, 0, -1, file_name, text)
        self.curr_char = None
        
        self.advance()
    
    def advance(self):
        """Move cursor forward by one and store current character in self.curr_char."""
        self.curr_pos.advance(self.curr_char)
        
        # check if curr position is valid index
        if self.curr_pos.idx < len(self.text):
            self.curr_char = self.text[self.curr_pos.idx]
        else:
            # reset cursor back to initial state
            self.curr_char = None
            
    def tokenize(self):
        """Create and return a list of tokens from self.text."""
        tokens = []
        
        while self.curr_char is not None:
            if self.curr_char in ' \t':
                self.advance()
            elif self.curr_char in NUM_CHARS:
                tokens.append(self.make_number())
            elif self.curr_char == '+':
                tokens.append(Token(TT_PLUS, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == '-':
                tokens.append(Token(TT_MINUS, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == '*':
                tokens.append(Token(TT_MUL, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == '/':
                tokens.append(Token(TT_DIV, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == '^':
                tokens.append(Token(TT_POW, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == '(':
                tokens.append(Token(TT_LPAREN, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == ')':
                tokens.append(Token(TT_RPAREN, start_pos=self.curr_pos))
                self.advance()
            else:
                # return error message
                start_pos = self.curr_pos.copy()
                illegal_char = self.curr_char
                self.advance()
                return [], IllegalCharError(start_pos, self.curr_pos, f"'{illegal_char}'")
        
        # add an EOF token to the end of token list
        tokens.append(Token(TT_EOF, start_pos=self.curr_pos))
        
        return tokens, None

    def make_number(self):
        """
        Convert a numeric string into a number, either int or float. Return a token that contains 
        this number.
        """
        num_str = ''
        dot_count = 0   # keep track of dot count in a numeric string to tell if it is an int or a float
        
        start_pos = self.curr_pos.copy()
        
        while (self.curr_char is not None) and (self.curr_char in NUM_CHARS):
            if self.curr_char == '.':
                if dot_count == 1: break    # can't have more than one dot in a number
                dot_count += 1
            num_str += self.curr_char 
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), start_pos=start_pos, end_pos=self.curr_pos)
        else:
            return Token(TT_FLOAT, float(num_str), start_pos=start_pos, end_pos=self.curr_pos)


############################################
# NODES
############################################

class NumberNode:
    def __init__(self, token):
        self.token = token
        
        self.start_pos = self.token.start_pos
        self.end_pos = self.token.end_pos
        
    def __repr__(self):
        return f'{self.token}'
    
class BinOpNode:
    def __init__(self, left_node, operator, right_node):
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node
        
        self.start_pos = self.left_node.start_pos
        self.end_pos = self.right_node.end_pos
    
    def __repr__(self):
        return f'({self.left_node}, {self.operator}, {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, operator, node):
        self.operator = operator
        self.node = node
        
        self.start_pos = self.operator.start_pos
        self.end_pos = self.node.end_pos
        
    def __repr__(self):
        return f'({self.operator}, {self.node})'


############################################
# PARSE RESULT
############################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, res):
        """Take in either a ParseResult or a node, and return the node."""
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        
        return res
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self
    

############################################
# PARSER
############################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        
        # set up token cursor
        self.token_index = -1
        self.advance()
    
    def advance(self):
        """Move token cursor forward by one and store current token into self.curr_token."""
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.curr_token = self.tokens[self.token_index]
        
        return self.curr_token
    
    ############################################
    
    # Components of an expression
    
    def _atom(self):
        """Create an atom node. See grammar.txt for reference"""
        parse_result = ParseResult()
        token = self.curr_token
        
        # check if this factor starts with an opening parenthesis
        if token.type == TT_LPAREN:
            parse_result.register(self.advance())
            expr = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            
            # looking to a closing parenthesis
            if self.curr_token.type == TT_RPAREN:
                parse_result.register(self.advance())
                return parse_result.success(expr)
            else:
                return parse_result.failure(InvalidSyntaxError(token.start_pos, 
                                                               token.end_pos, 
                                                               "Expected ')'"))
                
        # check if this factor is a valid int or float
        if token.type in (TT_INT, TT_FLOAT):
            parse_result.register(self.advance())
            return parse_result.success(NumberNode(token))
        
        return parse_result.failure(InvalidSyntaxError(token.start_pos,
                                                       token.end_pos,
                                                       "Expected int, float, '+', '-' or '('"))
        
    def _power(self):
        return self._bin_op(self._atom, (TT_POW, ), self._factor)
    
    def _factor(self):
        """Create a factor node. See grammar.txt for reference."""
        parse_result = ParseResult()
        token = self.curr_token
        
        # check if this factor starts with an unary operator
        if token.type in (TT_PLUS, TT_MINUS):
            parse_result.register(self.advance())
            factor = parse_result.register(self._factor())
            if parse_result.error: return parse_result
            return parse_result.success(UnaryOpNode(token, factor))
        
        return self._power()
    
    def _term(self):
        """Create a term node. See grammar.txt for reference."""
        return self._bin_op(self._factor, (TT_MUL, TT_DIV))
    
    def _expr(self):
        """Create a expression node. See grammar.txt for reference."""
        return self._bin_op(self._term, (TT_PLUS, TT_MINUS))
    
    def _bin_op(self, left_func, ops, right_func=None):
        if right_func is None: right_func = left_func
        
        parse_result = ParseResult()
        left = parse_result.register(left_func())
        
        if parse_result.error: return parse_result
        
        while self.curr_token.type in ops:
            operator = self.curr_token
            parse_result.register(self.advance())
            right = parse_result.register(right_func())
            
            # check error in each recursion iteration
            if parse_result.error: return parse_result
            
            left = BinOpNode(left, operator, right)
            
        return parse_result.success(left)
    
    ############################################
    
    def parse(self):
        """Generate an abstract syntax tree for the expression from the given list of tokens."""
        parse_result = self._expr()
        
        if (not parse_result.error) and (self.curr_token.type != TT_EOF):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected binary operator: '+', '-', '*', or '/'"))
        
        return parse_result
    

############################################
# VALUES
############################################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
        
    def set_pos(self, start_pos=None, end_pos=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self
    
    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        
    def subtract(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multiply(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divide_by(self, other):
        if isinstance(other, Number):
            # check if the divided is 0
            if other.value == 0:
                return None, RuntimeError_(other.start_pos, other.end_pos, 'Division by zero', self.context)
            
            return Number(self.value / other.value).set_context(self.context), None
        
    def power(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        
    def __repr__(self):
        return str(self.value)


############################################
# RUNTIME RESULT
############################################

class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None
        
    def register(self, result):
        if result.error: self.error = result.error
        return result.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self


############################################
# CONTEXT
############################################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos


############################################
# INTERPRETER
############################################

class Interpreter:
    def visit(self, node, context):
        """Walk through all the child nodes of the given node."""
        method_name = f'_visit_{type(node).__name__}'
        method = getattr(self, method_name, self._no_visit_method)
        
        return method(node, context)
    
    def _no_visit_method(self, node, context):
        raise Exception(f'No _visit_{type(node).__name__} method defined')
    
    def _visit_NumberNode(self, node, context):
        result = Number(node.token.value).set_context(context).set_pos(node.start_pos, node.end_pos)
        return RuntimeResult().success(result)
        
    def _visit_BinOpNode(self, node, context):
        runtime_result = RuntimeResult()
        left = runtime_result.register(self.visit(node.left_node, context))
        if runtime_result.error: return runtime_result
        right = runtime_result.register(self.visit(node.right_node, context))
        if runtime_result.error: return runtime_result
        
        # execute binary operations
        error = None
        if node.operator.type == TT_PLUS:
            result, error = left.add(right)
        elif node.operator.type == TT_MINUS:
            result, error = left.subtract(right)
        if node.operator.type == TT_MUL:
            result, error = left.multiply(right)
        if node.operator.type == TT_DIV:
            result, error = left.divide_by(right)
        if node.operator.type == TT_POW:
            result, error = left.power(right)
            
        if error:
            return runtime_result.failure(error)
        else:
            return runtime_result.success(result.set_pos(node.start_pos, node.end_pos))
        
    def _visit_UnaryOpNode(self, node, context):
        runtime_result = RuntimeResult()
        result = runtime_result.register(self.visit(node.node, context))
        if runtime_result.error: return runtime_result
        
        error = None
        if node.operator.type == TT_MINUS:
            result, error = Number(-result.value)
            
        if error:
            return runtime_result.failure(error)
        else:
            return runtime_result.success(result.set_pos(node.start_pos, node.end_pos))
    

############################################
# RUN
############################################

def run(file_name, text):
    """Return a list of tokens and error messages (None for no errors)."""
    lexer = Lexer(file_name, text)
    tokens, error = lexer.tokenize()
    if error: return None, error
    
    # generate an abstract syntax tree
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    
    # interpret the ast
    interpreter = Interpreter()
    context = Context('<main>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
