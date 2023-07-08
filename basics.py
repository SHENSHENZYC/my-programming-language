import string
from string_with_arrows import string_with_arrows


############################################
# CONSTANTS
############################################

NUM_CHARS = '0123456789.'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + '0123456789'


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
        

class ExpectedCharError(Error):
    def __init__(self, start_pos, end_pos, error_message):
        super(ExpectedCharError, self).__init__(start_pos, end_pos, 'ExpectedCharacterError', 'Expected ' + error_message)
        

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

# Numeric expression
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

# Variable assignment
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EQ = 'EQ'

# Comparison operators
TT_EE = 'EE'
TT_NE = 'NE'
TT_LT = 'LT'
TT_GT = 'GT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'

# Pre-assigned keywords
KEYWORDS = (
    'var', 
    'and', 
    'or', 
    'not', 
    'if', 
    'elif', 
    'then', 
    'else', 
    'for', 
    'to', 
    'step',
    'do',
    'while'
)


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
        
    def match(self, type_, value):
        """Check if the token matches given token type and value."""
        return self.type == type_ and self.value == value
        

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
                tokens.append(self._make_number())
            elif self.curr_char in LETTERS:
                tokens.append(self._make_identifier())
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
            elif self.curr_char == '=':
                tokens.append(self._make_eq())
                self.advance()
            elif self.curr_char == '!':
                token, error = self._make_neq()
                if error: return [], error
                tokens.append(token)
            elif self.curr_char == '<':
                tokens.append(self._make_lt())
                self.advance()
            elif self.curr_char == '>':
                tokens.append(self._make_gt())
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

    def _make_number(self):
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

    def _make_identifier(self):
        """Generate either an identifier or a keyword token."""
        id_str = ''
        start_pos = self.curr_pos.copy()
        
        while (self.curr_char is not None) and (self.curr_char in LETTERS_DIGITS + '_'):
            id_str += self.curr_char
            self.advance()
        
        # determine if id_str is an identifier or a keyword
        token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        
        return Token(token_type, id_str, start_pos=start_pos, end_pos=self.curr_pos)
    
    def _make_eq(self):
        """Generate either an assignment operator or a double equal operator token."""
        start_pos = self.curr_pos.copy()
        self.advance()
        
        if self.curr_char != '=':
            token_type = TT_EQ
        else:
            token_type = TT_EE
            self.advance()
            
        return Token(token_type, start_pos=start_pos, end_pos=self.curr_pos)
    
    def _make_neq(self):
        """Generate a not-equal operator token."""
        start_pos = self.curr_pos.copy()
        self.advance()
        
        if self.curr_char == '=':
            self.advance()
            return Token(TT_NE, start_pos=start_pos, end_pos=self.curr_pos), None
        
        self.advance()
        return None, ExpectedCharError(start_pos, self.curr_pos, "'=' after '!'")
        
    
    def _make_lt(self):
        """Generate either a less-than or a lte operator token."""
        start_pos = self.curr_pos.copy()
        self.advance()
        
        if self.curr_char != '=':
            token_type = TT_LT
        else:
            token_type = TT_LTE
            self.advance()
            
        return Token(token_type, start_pos=start_pos, end_pos=self.curr_pos)
    
    def _make_gt(self):
        """Generate either a greater-than or a gte operator token."""
        start_pos = self.curr_pos.copy()
        self.advance()
        
        if self.curr_char != '=':
            token_type = TT_GT
        else:
            token_type = TT_GTE
            self.advance()
            
        return Token(token_type, start_pos=start_pos, end_pos=self.curr_pos)
    

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
    

class VarAssignmentNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
        self.start_pos = self.var_name_token.start_pos
        self.end_pos = self.var_name_token.end_pos
    

class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token
        self.start_pos = self.var_name_token.start_pos
        self.end_pos = self.var_name_token.end_pos
        

class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case
        self.start_pos = self.cases[0][0].start_pos
        
        if self.else_case:
            self.end_pos = self.else_case.end_pos
        else:
            self.end_pos = self.cases[-1][0].end_pos
            

class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, body_node, step_value_node=None):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.body_node = body_node
        self.step_value_node = step_value_node
        
        self.start_pos = self.var_name_token.start_pos
        self.end_pos = self.body_node.end_pos
        

class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node
        
        self.start_pos = self.condition_node.start_pos
        self.end_pos = self.body_node.end_pos


############################################
# PARSE RESULT
############################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        
    def register_advancement(self):
        self.advance_count += 1
        
    def register(self, res):
        """Take in a ParseResult, and return the node."""
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if (not self.error) or (self.advance_count == 0):
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
    
    def _if_expr(self):
        """Create an expression node for if statement. See grammar.txt for reference"""
        parse_result = ParseResult()
        cases = []
        else_case = None
        
        if not self.curr_token.match(TT_KEYWORD, 'if'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'if'"))
            
        parse_result.register_advancement()
        self.advance()
        
        condition = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        if not self.curr_token.match(TT_KEYWORD, 'then'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'then'"))
            
        parse_result.register_advancement()
        self.advance()
        
        expr = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        cases.append((condition, expr))
        
        while self.curr_token.match(TT_KEYWORD, 'elif'):
            parse_result.register_advancement()
            self.advance()
            
            condition = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            
            if not self.curr_token.match(TT_KEYWORD, 'then'):
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'then'"))
            
            parse_result.register_advancement()
            self.advance()
            
            expr = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            cases.append((condition, expr))
        
        if self.curr_token.match(TT_KEYWORD, 'else'):
            parse_result.register_advancement()
            self.advance()
            
            else_case = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            
        return parse_result.success(IfNode(cases, else_case))
    
    def _for_expr(self):
        """Create an expression node for for loop statement. See grammar.txt for reference"""
        parse_result = ParseResult()
        
        if not self.curr_token.match(TT_KEYWORD, 'for'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'for'"))
        
        parse_result.register_advancement()
        self.advance()
        
        if self.curr_token.type != TT_IDENTIFIER:
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected identifier"))
        
        var_name = self.curr_token
        parse_result.register_advancement()
        self.advance()
        
        if self.curr_token.type != TT_EQ:
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected '='"))
            
        parse_result.register_advancement()
        self.advance()
        start_value = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        if not self.curr_token.match(TT_KEYWORD, 'to'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'to'"))
            
        parse_result.register_advancement()
        self.advance()
        end_value = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        step_value = None
        if self.curr_token.match(TT_KEYWORD, 'step'):
            parse_result.register_advancement()
            self.advance()
            step_value = parse_result.register(self._expr())
            if parse_result.error: return parse_result
        
        if not self.curr_token.match(TT_KEYWORD, 'do'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'do'"))
            
        parse_result.register_advancement()
        self.advance()
        body = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        return parse_result.success(ForNode(var_name, start_value, end_value, body, step_value))
        
    
    def _while_expr(self):
        """Create an expression node for while loop statement. See grammar.txt for reference"""
        parse_result = ParseResult()
        
        if not self.curr_token.match(TT_KEYWORD, 'while'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'while'"))
            
        parse_result.register_advancement()
        self.advance()
        condition = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        if not self.curr_token.match(TT_KEYWORD, 'do'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'do'"))
            
        parse_result.register_advancement()
        self.advance()
        body = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        return parse_result.success(WhileNode(condition, body))

    def _atom(self):
        """Create an atom node. See grammar.txt for reference"""
        parse_result = ParseResult()
        token = self.curr_token
        
        # check if this atom starts with an opening parenthesis
        if token.type == TT_LPAREN:
            parse_result.register_advancement()
            self.advance()
            expr = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            
            # looking to a closing parenthesis
            if self.curr_token.type == TT_RPAREN:
                parse_result.register_advancement()
                self.advance()
                return parse_result.success(expr)
            else:
                return parse_result.failure(InvalidSyntaxError(token.start_pos, 
                                                               token.end_pos, 
                                                               "Expected ')'"))
                
        # check if this atom is a valid int or float
        if token.type in (TT_INT, TT_FLOAT):
            parse_result.register_advancement()
            self.advance()
            return parse_result.success(NumberNode(token))
        
        # check if this atom is an existing identifier
        if token.type == TT_IDENTIFIER:
            parse_result.register_advancement()
            self.advance()
            return parse_result.success(VarAccessNode(token))
        
        # check if this atom is an if expression
        if token.match(TT_KEYWORD, 'if'):
            if_expr = parse_result.register(self._if_expr())
            if parse_result.error: return parse_result
            return parse_result.success(if_expr)
        
        # check if this atom is a for expression
        if token.match(TT_KEYWORD, 'for'):
            for_expr = parse_result.register(self._for_expr())
            if parse_result.error: return parse_result
            return parse_result.success(for_expr)
        
        # check if this atom is a while expression
        if token.match(TT_KEYWORD, 'while'):
            while_expr = parse_result.register(self._while_expr())
            if parse_result.error: return parse_result
            return parse_result.success(while_expr)
        
        return parse_result.failure(InvalidSyntaxError(token.start_pos,
                                                       token.end_pos,
                                                       "Expected int, float, identifier, '+', '-' or '('"))
        
    def _power(self):
        return self._bin_op(self._atom, (TT_POW, ), self._factor)
    
    def _factor(self):
        """Create a factor node. See grammar.txt for reference."""
        parse_result = ParseResult()
        token = self.curr_token
        
        # check if this factor starts with an unary operator
        if token.type in (TT_PLUS, TT_MINUS):
            parse_result.register_advancement()
            self.advance()
            factor = parse_result.register(self._factor())
            if parse_result.error: return parse_result
            return parse_result.success(UnaryOpNode(token, factor))
        
        return self._power()
    
    def _term(self):
        """Create a term node. See grammar.txt for reference."""
        return self._bin_op(self._factor, (TT_MUL, TT_DIV))
    
    def _arith_expr(self):
        """Create an expression node for arithmetic operators. See grammar.txt for reference."""
        return self._bin_op(self._term, (TT_PLUS, TT_MINUS))
    
    def _comp_expr(self):
        """Create an expression node for comparison operators. See grammar.txt for reference."""
        parse_result = ParseResult()
        
        # looking for keyword 'not'
        if self.curr_token.match(TT_KEYWORD, 'not'):
            operator = self.curr_token
            parse_result.register_advancement()
            self.advance()
            
            comp_expr = parse_result.register(self._comp_expr())
            if parse_result.error: return parse_result
            
            return parse_result.success(UnaryOpNode(operator, comp_expr))
        
        comp_ops = (TT_EE, TT_NE, TT_LT, TT_LTE, TT_GT, TT_GTE)
        comp_expr = parse_result.register(self._bin_op(self._arith_expr, comp_ops))
        if parse_result.error:
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos,
                                                           self.curr_token.end_pos, 
                                                           "Expected int, float, identifier, 'not', '+', '-' or '('"))
        
        return parse_result.success(comp_expr)
    
    def _expr(self):
        """Create an overall expression node. See grammar.txt for reference."""
        parse_result = ParseResult()
        
        # looking for keyword 'var'
        if self.curr_token.match(TT_KEYWORD, 'var'):
            parse_result.register_advancement()
            self.advance()
            # check if next token is an identifier
            if self.curr_token.type != TT_IDENTIFIER:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                        self.curr_token.end_pos, 
                                                        'Expected identifier'))
            var_name = self.curr_token
            
            parse_result.register_advancement()
            self.advance()
            # check if next token is an equal sign
            if self.curr_token.type != TT_EQ:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                        self.curr_token.end_pos, 
                                                        "Expected '='"))
                
            parse_result.register_advancement()
            self.advance()
            expr = parse_result.register(self._expr())
            
            if parse_result.error: return parse_result
            return parse_result.success(VarAssignmentNode(var_name, expr))
             
        
        expr = parse_result.register(self._bin_op(self._comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))
        if parse_result.error: 
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos,
                                                           self.curr_token.end_pos,
                                                           "Expected int, float, identifier, 'var', '+', '-' or '('"))
        
        return parse_result.success(expr)
    
    def _bin_op(self, left_func, ops, right_func=None):
        if right_func is None: right_func = left_func
        
        parse_result = ParseResult()
        left = parse_result.register(left_func())
        
        if parse_result.error: return parse_result
        
        while (self.curr_token.type in ops) or ((self.curr_token.type, self.curr_token.value) in ops):
            operator = self.curr_token
            parse_result.register_advancement()
            self.advance()
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
        
    def eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        
    def neq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        
    def lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        
    def lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        
    def gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        
    def gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        
    def and_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        
    def or_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        
    def not_(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    
    def is_true(self):
        return self.value != 0
        
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.start_pos, self.end_pos).set_context(self.context)
        return copy
        
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
        self.symbol_table = None
        

############################################
# SYMBOL TABLE
############################################

class SymbolTable:
    def __init__(self):
        self.symbols = dict()
        self.parent = None  # to keep track of the stack frame that holds all variables in the symbol table
    
    def get(self, var_name):
        value = self.symbols.get(var_name, None)
        
        if (value is None) and self.parent:
            return self.parent.get(var_name, None)
        
        return value
    
    def set(self, var_name, value):
        self.symbols[var_name] = value
        
    def remove(self, var_name):
        del self.symbols[var_name]


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
        elif node.operator.type == TT_MUL:
            result, error = left.multiply(right)
        elif node.operator.type == TT_DIV:
            result, error = left.divide_by(right)
        elif node.operator.type == TT_POW:
            result, error = left.power(right)
        elif node.operator.type == TT_EE:
            result, error = left.eq(right)
        elif node.operator.type == TT_NE:
            result, error = left.neq(right)
        elif node.operator.type == TT_LT:
            result, error = left.lt(right)
        elif node.operator.type == TT_LTE:
            result, error = left.lte(right)
        elif node.operator.type == TT_GT:
            result, error = left.gt(right)
        elif node.operator.type == TT_GTE:
            result, error = left.gte(right)
        elif node.operator.match(TT_KEYWORD, 'and'):
            result, error = left.and_(right)
        elif node.operator.match(TT_KEYWORD, 'or'):
            result, error = left.or_(right)
            
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
            result, error = result.multiply(Number(-1))
        elif node.operator.match(TT_KEYWORD, 'not'):
            result, error = result.not_()
            
        if error:
            return runtime_result.failure(error)
        else:
            return runtime_result.success(result.set_pos(node.start_pos, node.end_pos))
        
    def _visit_VarAssignmentNode(self, node, context):
        runtime_result = RuntimeResult()
        var_name = node.var_name_token.value
        value = runtime_result.register(self.visit(node.value_node, context))
        
        if runtime_result.error: return runtime_result
        
        context.symbol_table.set(var_name, value)
        return runtime_result.success(value)
        
    def _visit_VarAccessNode(self, node, context):
        runtime_result = RuntimeResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
        
        if not value:
            return runtime_result.failure(RuntimeError_(node.start_pos, 
                                                        node.end_pos, 
                                                        f"'{var_name}' is not defined", 
                                                        context))
        
        # reassign the value with starting and ending position when accessed
        value = value.copy().set_pos(node.start_pos, node.end_pos)
        
        return runtime_result.success(value)       
    
    def _visit_IfNode(self, node, context):
        runtime_result = RuntimeResult()
        
        for condition, expr in node.cases:
            condition_value = runtime_result.register(self.visit(condition, context))
            if runtime_result.error: return runtime_result
            
            if condition_value.is_true():
                expr_value = runtime_result.register(self.visit(expr, context))
                if runtime_result.error: return runtime_result
                return runtime_result.success(expr_value)
        
        if node.else_case:
            else_case_value = runtime_result.register(self.visit(node.else_case, context))
            if runtime_result.error: return runtime_result
            return runtime_result.success(else_case_value)
        
        return runtime_result.success(None)
    
    def _visit_ForNode(self, node, context):
        runtime_result = RuntimeResult()
        
        start_value = runtime_result.register(self.visit(node.start_value_node, context))
        if runtime_result.error: return runtime_result
        
        end_value = runtime_result.register(self.visit(node.end_value_node, context))
        if runtime_result.error: return runtime_result
        
        step_value = Number(1)  # default value for step
        if node.step_value_node:
            step_value = runtime_result.register(self.visit(node.step_value_node, context))
            if runtime_result.error: return runtime_result
            
        i = start_value.value
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
            
        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value
            runtime_result.register(self.visit(node.body_node, context))
            if runtime_result.error: return runtime_result
        
        return runtime_result.success(None)
        
    def _visit_WhileNode(self, node, context):
        runtime_result = RuntimeResult()
        
        while True:
            condition_value = runtime_result.register(self.visit(node.condition_node, context))
            if runtime_result.error: return runtime_result

            if not condition_value.is_true(): break
            
            runtime_result.register(self.visit(node.body_node, context))
            if runtime_result.error: return runtime_result
        
        return runtime_result.success(None)

############################################
# RUN
############################################

# set up symbol table for global variables
global_symbol_table = SymbolTable()
global_symbol_table.set('null', Number(0))
global_symbol_table.set('false', Number(0))
global_symbol_table.set('true', Number(1))


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
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
