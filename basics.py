import string
import os
import math
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
TT_STRING = 'STRING'
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
TT_NEWLINE = 'NEWLINE'
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

# Function-related tokens
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'

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
    'while', 
    'func', 
    'end'
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
                tokens.append(self._make_minus_or_arrow())
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
            elif self.curr_char == ',':
                tokens.append(Token(TT_COMMA, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == '"':
                tokens.append(self._make_string())
            elif self.curr_char == '[':
                tokens.append(Token(TT_LSQUARE, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char == ']':
                tokens.append(Token(TT_RSQUARE, start_pos=self.curr_pos))
                self.advance()
            elif self.curr_char in ';\n':
                tokens.append(Token(TT_NEWLINE, start_pos=self.curr_pos))
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
    
    def _make_minus_or_arrow(self):
        """Generate either a minus operator token or an arrow token."""
        start_pos = self.curr_pos.copy()
        self.advance()
        
        if self.curr_char != '>':
            token_type = TT_MINUS
        else:
            token_type = TT_ARROW
            self.advance()
        
        return Token(token_type, start_pos=start_pos, end_pos=self.curr_pos)
    
    def _make_string(self):
        """Generate a string token."""
        string = ''
        start_pos = self.curr_pos.copy()        
        escape_char = False
        self.advance()
        
        escape_character_dict = {
            'n': '\n', 
            't': '\t', 
            'r': '\r'
        }
        
        while (self.curr_char is not None) and ((self.curr_char != '"') or escape_char):
            # allow escape characters \n, \t, \r in a string
            if escape_char:
                string += escape_character_dict.get(self.curr_char, self.curr_char)
                escape_char = False
                self.advance()
                continue

            if self.curr_char == '\\':
                escape_char = True
            else:
                string += self.curr_char
            self.advance()
                        
        self.advance()
        
        return Token(TT_STRING, string, start_pos=start_pos, end_pos=self.curr_pos)

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
    

class StringNode:
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
            self.end_pos = self.else_case[0].end_pos
        else:
            self.end_pos = self.cases[-1][0].end_pos
            

class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, body_node, step_value_node, should_return_null):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.body_node = body_node
        self.step_value_node = step_value_node
        self.should_return_null = should_return_null
        
        self.start_pos = self.var_name_token.start_pos
        self.end_pos = self.body_node.end_pos
        

class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null
        
        self.start_pos = self.condition_node.start_pos
        self.end_pos = self.body_node.end_pos


class FuncDefinitionNode:
    def __init__(self, func_name_token, arg_name_tokens, body_node, should_return_null):
        self.func_name_token = func_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node
        self.should_return_null = should_return_null
        
        if self.func_name_token:
            self.start_pos = self.func_name_token.start_pos
        elif len(self.arg_name_tokens) > 0:
            self.start_pos = self.arg_name_tokens[0].start_pos
        else:
            self.start_pos = self.body_node.start_pos
        
        self.end_pos = self.body_node.end_pos
        

class FuncCallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        
        self.start_pos = self.node_to_call.start_pos
        
        if len(self.arg_nodes) > 0:
            self.end_pos = self.arg_nodes[-1].end_pos
        else:
            self.end_pos = self.node_to_call.end_pos
            
            
class ListNode:
    def __init__(self, element_nodes, start_pos, end_pos):
        self.element_nodes = element_nodes
        self.start_pos = start_pos
        self.end_pos = end_pos


############################################
# PARSE RESULT
############################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.last_registered_advance_count = 0
        self.to_register_count = 0
        
    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1
        
    def register(self, res):
        """Take in a ParseResult, and return the node."""
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.last_registered_advance_count
            return None
        return self.register(res)
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if (not self.error) or (self.last_registered_advance_count == 0):
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
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.curr_token = self.tokens[self.token_index]
        
        return self.curr_token
    
    def reverse(self, amount=1):
        """Move token cursor backward by amount and store current token into self.curr_token."""
        self.token_index -= amount
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.curr_token = self.tokens[self.token_index]
        
        return self.curr_token
    
    ############################################
    
    # Components of a statement
    
    def _list_expr(self):
        """Create an list node. See grammar.txt for reference"""
        parse_result = ParseResult()
        element_nodes = []
        start_pos = self.curr_token.start_pos.copy()
        
        if self.curr_token.type != TT_LSQUARE:
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected '['"))
            
        parse_result.register_advancement()
        self.advance()
        
        if self.curr_token.type == TT_RSQUARE:
            parse_result.register_advancement()
            self.advance()
        else:
            element_nodes.append(parse_result.register(self._expr()))
            if parse_result.error:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                                self.curr_token.end_pos, 
                                                                "Expected 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[', ']', or 'not'"))

            while self.curr_token.type == TT_COMMA:
                parse_result.register_advancement()
                self.advance()
                
                element_nodes.append(parse_result.register(self._expr()))
                if parse_result.error: return parse_result
            
            if self.curr_token.type != TT_RSQUARE:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                                self.curr_token.end_pos, 
                                                                "Expected ',' or ']'"))
            
            parse_result.register_advancement()
            self.advance()
        
        return parse_result.success(ListNode(element_nodes, start_pos, self.curr_token.end_pos.copy()))
            
    
    def _if_expr(self):
        """Create an expression node for if statement. See grammar.txt for reference"""
        parse_result = ParseResult()
        
        all_cases = parse_result.register(self._if_expr_cases('if'))
        if parse_result.error: return parse_result
        cases, else_case = all_cases
        
        return parse_result.success(IfNode(cases, else_case))
    
    def _elif_expr(self):
        return self._if_expr_cases('elif')
    
    def _else_expr(self):
        parse_result = ParseResult()
        else_case = None
        
        if self.curr_token.match(TT_KEYWORD, 'else'):
            parse_result.register_advancement()
            self.advance()
            
            if self.curr_token.type == TT_NEWLINE:
                parse_result.register_advancement()
                self.advance()
                
                statements = parse_result.register(self._statement())
                if parse_result.error: return parse_result
                else_case = (statements, True)
                
                if self.curr_token.match(TT_KEYWORD, 'end'):
                    parse_result.register_advancement()
                    self.advance()
                else:
                    return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                                   self.curr_token.end_pos, 
                                                                   "Expected keyword 'end'"))
            
            else:
                expr = parse_result.register(self._expr())
                if parse_result.error: return parse_result
                else_case = (expr, False)
                
        return parse_result.success(else_case)
    
    def _elif_or_else_expr(self):
        parse_result = ParseResult()
        cases = []
        else_case = None
        
        if self.curr_token.match(TT_KEYWORD, 'elif'):
            all_cases = parse_result.register(self._elif_expr())
            if parse_result.error: return parse_result
            cases, else_case = all_cases
        else:
            else_case = parse_result.register(self._else_expr())
            if parse_result.error: return parse_result
            
        return parse_result.success((cases, else_case))
    
    def _if_expr_cases(self, case_keyword):
        """
        Create an node for different parts of an if statement: if or elif, depending on
        given keyword.
        """
        parse_result = ParseResult()
        cases = []
        else_case = None
        
        if not self.curr_token.match(TT_KEYWORD, case_keyword):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           f"Expected keyword '{case_keyword}'"))
        
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
        
        if self.curr_token.type == TT_NEWLINE:
            parse_result.register_advancement()
            self.advance()
            
            statements = parse_result.register(self._statement())
            if parse_result.error: return parse_result
            cases.append((condition, statements, True))
            
            if self.curr_token.match(TT_KEYWORD, 'end'):
                parse_result.register_advancement()
                self.advance()
            else:
                all_cases = parse_result.register(self._elif_or_else_expr())
                if parse_result.error: return parse_result
                new_cases, else_cases = all_cases
                cases.extend(new_cases)
        
        else:
            expr = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            cases.append((condition, expr, False))
            
            all_cases = parse_result.register(self._elif_or_else_expr())
            if parse_result.error: return parse_result
            new_cases, else_cases = all_cases
            cases.extend(new_cases)
            
        return parse_result.success((cases, else_case))
    
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
        
        if self.curr_token.type == TT_NEWLINE:
            parse_result.register_advancement()
            self.advance()
            
            body = parse_result.register(self._statement())
            if parse_result.error: return parse_result
            
            if not self.curr_token.match(TT_KEYWORD, 'end'):
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                               self.curr_token.end_pos, 
                                                               "Expected keyword 'end'")) 

            parse_result.register_advancement()
            self.advance()
            
            return parse_result.success(ForNode(var_name, start_value, end_value, body, step_value, True))
        
        body = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        return parse_result.success(ForNode(var_name, start_value, end_value, body, step_value, False))
        
    
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
        
        if self.curr_token.type == TT_NEWLINE:
            parse_result.register_advancement()
            self.advance()
            
            body = parse_result.register(self._statement())
            if parse_result.error: return parse_result
            
            if not self.curr_token.match(TT_KEYWORD, 'end'):
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                               self.curr_token.end_pos, 
                                                               "Expected keyword 'end'")) 

            parse_result.register_advancement()
            self.advance()
            
            return parse_result.success(WhileNode(condition, body, True))
        
        body = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        
        return parse_result.success(WhileNode(condition, body, False))
    
    def _func_def(self):
        """Create a node for defining a function. See grammar.txt for reference"""
        parse_result = ParseResult()
        
        if not self.curr_token.match(TT_KEYWORD, 'func'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'func'"))
            
        parse_result.register_advancement()
        self.advance()

        if self.curr_token.type == TT_IDENTIFIER:
            func_name_token = self.curr_token
            parse_result.register_advancement()
            self.advance()
            
            if self.curr_token.type != TT_LPAREN:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                               self.curr_token.end_pos, 
                                                               "Expected '('"))
        else:
            func_name_token = None
            if self.curr_token.type != TT_LPAREN:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                               self.curr_token.end_pos, 
                                                               "Expected identifier or '('"))
                
        parse_result.register_advancement()
        self.advance()
        arg_name_tokens = []
        
        if self.curr_token.type == TT_IDENTIFIER:
            arg_name_tokens.append(self.curr_token)
            parse_result.register_advancement()
            self.advance()
            
            while self.curr_token.type == TT_COMMA:
                parse_result.register_advancement()
                self.advance()
                
                if self.curr_token.type != TT_IDENTIFIER:
                    return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                                   self.curr_token.end_pos, 
                                                                   "Expected identifier"))
                
                arg_name_tokens.append(self.curr_token)
                parse_result.register_advancement()
                self.advance()
        
            if self.curr_token.type != TT_RPAREN:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                               self.curr_token.end_pos, 
                                                               "Expected ',' or ')'"))
        
        else:
            if self.curr_token.type != TT_RPAREN:
                return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                               self.curr_token.end_pos, 
                                                               "Expected identifier or ')'"))
        
        parse_result.register_advancement()
        self.advance()
        
        if self.curr_token.type == TT_ARROW:
            parse_result.register_advancement()
            self.advance()
            
            body_expr = parse_result.register(self._expr())
            if parse_result.error: return parse_result
            
            return parse_result.success(FuncDefinitionNode(func_name_token, arg_name_tokens, body_expr, False))
        
        if self.curr_token.type != TT_NEWLINE:
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos,
                                                           self.curr_token.end_pos,
                                                           "Expected '->' or newline character")) 
            
        parse_result.register_advancement()
        self.advance()
        
        body = parse_result.register(self._statement())
        if parse_result.error: return parse_result
        
        if not self.curr_token.match(TT_KEYWORD, 'end'):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected keyword 'end'")) 

        parse_result.register_advancement()
        self.advance()
        
        return parse_result.success(FuncDefinitionNode(func_name_token, arg_name_tokens, body_expr, True))
            
        

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
        
        # check if this atom is a string
        if token.type == TT_STRING:
            parse_result.register_advancement()
            self.advance()
            return parse_result.success(StringNode(token))
        
        # check if this atom is an existing identifier
        if token.type == TT_IDENTIFIER:
            parse_result.register_advancement()
            self.advance()
            return parse_result.success(VarAccessNode(token))
        
        # check if this atom is a list
        if token.type == TT_LSQUARE:
            list_expr = parse_result.register(self._list_expr())
            if parse_result.error: return parse_result
            return parse_result.success(list_expr)
        
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
        
        # check if this atom is a function
        if token.match(TT_KEYWORD, 'func'):
            while_expr = parse_result.register(self._func_def())
            if parse_result.error: return parse_result
            return parse_result.success(while_expr)
        
        return parse_result.failure(InvalidSyntaxError(token.start_pos,
                                                       token.end_pos,
                                                       "Expected 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', or '['"))
        
    def _call(self):
        """Create a node for calling a function. See grammar.txt for reference."""
        parse_result = ParseResult()
        atom = parse_result.register(self._atom())
        if parse_result.error: return parse_result
        
        if self.curr_token.type == TT_LPAREN:
            parse_result.register_advancement()
            self.advance()
            arg_nodes = []
            
            if self.curr_token.type == TT_RPAREN:
                parse_result.register_advancement()
                self.advance()
            else:
                arg_nodes.append(parse_result.register(self._expr()))
                if parse_result.error:
                    return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                                   self.curr_token.end_pos, 
                                                                   "Expected 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', ')', '[', or 'not'"))

                while self.curr_token.type == TT_COMMA:
                    parse_result.register_advancement()
                    self.advance()
                    
                    arg_nodes.append(parse_result.register(self._expr()))
                    if parse_result.error: return parse_result
                
                if self.curr_token.type != TT_RPAREN:
                    return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                                   self.curr_token.end_pos, 
                                                                   "Expected ',' or ')'"))
                
                parse_result.register_advancement()
                self.advance()
        
            return parse_result.success(FuncCallNode(atom, arg_nodes))
        return parse_result.success(atom)
        
    def _power(self):
        """Create a node for power expression. See grammar.txt for reference."""
        return self._bin_op(self._call, (TT_POW, ), self._factor)
    
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
                                                           "Expected int, float, identifier, '+', '-', '(', '[', or 'not'"))
        
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
                                                           "Expected 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[', or 'not'"))
        
        return parse_result.success(expr)
    
    def _statement(self):
        parse_result = ParseResult()
        statements = []
        start_pos = self.curr_token.start_pos.copy()
        
        # check if the current token is a newline character
        while self.curr_token.type == TT_NEWLINE:
            parse_result.register_advancement()
            self.advance()
            
        statement = parse_result.register(self._expr())
        if parse_result.error: return parse_result
        statements.append(statement)
        
        # set up a flag to determine if this is a multi-line statement
        more_statements = True
        while True:
            newline_count = 0
            while self.curr_token.type == TT_NEWLINE:
                parse_result.register_advancement()
                self.advance()
                newline_count += 1
            
            if newline_count == 0:
                more_statements = False
            
            if not more_statements: break
            statement = parse_result.try_register(self._expr())
            if not statement:
                self.reverse(parse_result.to_reverse_count)
                more_statements = False
                continue
        
            statements.append(statement)
        
        return parse_result.success(ListNode(statements, start_pos, self.curr_token.start_pos.copy()))
    
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
        parse_result = self._statement()
        
        if (not parse_result.error) and (self.curr_token.type != TT_EOF):
            return parse_result.failure(InvalidSyntaxError(self.curr_token.start_pos, 
                                                           self.curr_token.end_pos, 
                                                           "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'and' or 'or'"))
        
        return parse_result
    

############################################
# VALUES
############################################

class Value:
    def __init__(self):
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
        return None, self.illegal_operation(other)
    
    def subtract(self, other):
        return None, self.illegal_operation(other)
    
    def multiply(self, other):
        return None, self.illegal_operation(other)
    
    def divide_by(self, other):
        return None, self.illegal_operation(other)
    
    def power(self, other):
        return None, self.illegal_operation(other)
    
    def eq(self, other):
        return None, self.illegal_operation(other)
    
    def neq(self, other):
        return None, self.illegal_operation(other)
    
    def lt(self, other):
        return None, self.illegal_operation(other)
    
    def lte(self, other):
        return None, self.illegal_operation(other)
    
    def gt(self, other):
        return None, self.illegal_operation(other)
    
    def gte(self, other):
        return None, self.illegal_operation(other)
    
    def and_(self, other):
        return None, self.illegal_operation(other)
    
    def or_(self, other):
        return None, self.illegal_operation(other)
    
    def not_(self, other):
        return None, self.illegal_operation(other)
    
    def execute(self, args):
        return RuntimeResult().failure(self.illegal_operation())
    
    def copy(self):
        raise Exception('No copy method defined')
    
    def is_true(self):
        return False
    
    def illegal_operation(self, other=None):
        if not other: other = self
        return RuntimeError_(self.start_pos, self.end_pos, 'IllegalOperationError', self.context)


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def subtract(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def multiply(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def divide_by(self, other):
        if isinstance(other, Number):
            # check if the divided is 0
            if other.value == 0:
                return None, RuntimeError_(other.start_pos, other.end_pos, 'Division by zero', self.context)
            
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def power(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def neq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def and_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def or_(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
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


# define some constants in the language
Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        
    def add(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def multiply(self, other):
        if isinstance(other, Number):
            return String(self.value * int(other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.start_pos, self.end_pos)
        
    def is_true(self):
        return len(self.value) > 0
    
    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.start_pos, self.end_pos).set_context(self.context)
        return copy
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f'"{self.value}"'


class BaseFunction(Value):
    def __init__(self, func_name):
        super().__init__()
        self.func_name = func_name if func_name else '<default_func>'
        
    def generate_func_context(self):
        func_context = Context(self.func_name, self.context, self.start_pos)
        func_context.symbol_table = SymbolTable(func_context.parent.symbol_table)
        return func_context
    
    def _check_args(self, arg_names, args):
        runtime_result = RuntimeResult()
        if len(args) > len(arg_names):
            return runtime_result.failure(RuntimeError_(self.start_pos, self.end_pos,
                                                        f'{len(args) - len(arg_names)} too many arguments passed into {self.func_name}', 
                                                        self.context))
            
        if len(args) < len(arg_names):
            return runtime_result.failure(RuntimeError_(self.start_pos, self.end_pos,
                                                        f'{len(arg_names) - len(args)} too few arguments passed into {self.func_name}', 
                                                        self.context))
            
        return runtime_result.success(None)
    
    def _populate_args(self, arg_names, args, func_context):
        for arg_name, arg_value in zip(arg_names, args):
            arg_value.set_context(func_context)
            func_context.symbol_table.set(arg_name, arg_value)
            
    def check_and_populate_args(self, arg_names, args, func_context):
        runtime_result = RuntimeResult()
        runtime_result.register(self._check_args(arg_names, args))
        if runtime_result.error: return runtime_result
        
        self._populate_args(arg_names, args, func_context)
        
        return runtime_result.success(None)

class Function(BaseFunction):
    def __init__(self, func_name, arg_names, body_node, should_return_null):
        super().__init__(func_name)
        self.arg_names = arg_names
        self.body_node = body_node
        self.should_return_null = should_return_null
        
    def execute(self, args):
        runtime_result = RuntimeResult()
        interpreter = Interpreter()
        
        # create a new context for the function call
        func_context = self.generate_func_context()
        
        # check if number of passed arguments match number of required arguments by function
        runtime_result.register(self.check_and_populate_args(self.arg_names, args, func_context))
        if runtime_result.error: return runtime_result
        
        value = runtime_result.register(Interpreter().visit(self.body_node, func_context))
        if runtime_result.error: return runtime_result
        
        return runtime_result.success(Number.null if self.should_return_null else value)

    def copy(self):
        copy = Function(self.func_name, self.arg_names, self.body_node, self.should_return_null)
        copy.set_pos(self.start_pos, self.end_pos).set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'<function {self.func_name}>'
    

class BuiltInFunction(BaseFunction):
    def __init__(self, func_name):
        super().__init__(func_name)
        
    def execute(self, args):
        runtime_result = RuntimeResult()
        func_context = self.generate_func_context()
        
        method_name = f'execute_{self.func_name}'
        method = getattr(self, method_name, self._no_visit_method)
        
        runtime_result.register(self.check_and_populate_args(method.arg_names, args, func_context))
        if runtime_result.error: return runtime_result
        
        return_value = runtime_result.register(method(func_context))
        if runtime_result.error: return runtime_result
        
        return runtime_result.success(return_value)
        
    def _no_visit_method(self, node, context):
        raise Exception(f'No _visit_{self.func_name} method defined')
    
    def copy(self):
        copy = BuiltInFunction(self.func_name)
        copy.set_pos(self.start_pos, self.end_pos).set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'<built-in function {self.func_name}>'
    
    ############################################
    
    # Built-in functions
    
    def execute_print(self, func_context):
        print(str(func_context.symbol_table.get('value')))
        return RuntimeResult().success(Number.null)
    execute_print.arg_names = ['value']
  
    def execute_print_ret(self, func_context):
        return RuntimeResult().success(String(str(func_context.symbol_table.get('value'))))
    execute_print_ret.arg_names = ['value']
  
    def execute_input(self, func_context):
        text = input()
        return RuntimeResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, func_context):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RuntimeResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, func_context):
        os.system('cls' if os.name == 'nt' else 'clear') 
        return RuntimeResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, func_context):
        is_number = isinstance(func_context.symbol_table.get("value"), Number)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, func_context):
        is_number = isinstance(func_context.symbol_table.get("value"), String)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, func_context):
        is_number = isinstance(func_context.symbol_table.get("value"), List)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, func_context):
        is_number = isinstance(func_context.symbol_table.get("value"), BaseFunction)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_function.arg_names = ["value"]

    def execute_append(self, func_context):
        list_ = func_context.symbol_table.get("list")
        value = func_context.symbol_table.get("value")

        if not isinstance(list_, List):
            return RuntimeResult().failure(RuntimeError_(
                self.start_pos, self.end_pos,
                "First argument must be list",
                func_context
            ))

        list_.elements.append(value)
        return RuntimeResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, func_context):
        list_ = func_context.symbol_table.get("list")
        index = func_context.symbol_table.get("index")

        if not isinstance(list_, List):
            return RuntimeResult().failure(RuntimeError_(
                self.start_pos, self.end_pos,
                "First argument must be list",
                func_context
            ))

        if not isinstance(index, Number):
            return RuntimeResult().failure(RuntimeError_(
                self.start_pos, self.end_pos,
                "Second argument must be number",
                func_context
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RuntimeResult().failure(RuntimeError_(
                self.start_pos, self.end_pos,
                'Element at this index could not be removed from list because index is out of bounds',
                func_context
            ))
        return RuntimeResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, func_context):
        listA = func_context.symbol_table.get("listA")
        listB = func_context.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RuntimeResult().failure(RuntimeError_(
                self.start_pos, self.end_pos,
                "First argument must be list",
                func_context
            ))

        if not isinstance(listB, List):
            return RuntimeResult().failure(RuntimeError_(
                self.start_pos, self.end_pos,
                "Second argument must be list",
                func_context
            ))

        listA.elements.extend(listB.elements)
        return RuntimeResult().success(Number.null)
    execute_extend.arg_names = ["listA", "listB"]

# define constants for built-in function names
BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        
    def add(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def subtract(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RuntimeError_(other.start_pos, other.end_pos,
                                           'Element at this index could not be removed from list because index is out of bounds',
                                           self.context)
        else:
            return None, Value.illegal_operation(self, other)
    
    def multiply(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
        
    def divide_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RuntimeError_(other.start_pos, other.end_pos,
                                           'Element at this index could not be retrieved from list because index is out of bounds',
                                           self.context)
        else:
            return None, Value.illegal_operation(self, other)
        
    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.start_pos, self.end_pos).set_context(self.context)
        return copy
    
    def __str__(self):
        return ", ".join([str(elem) for elem in self.elements])
    
    def __repr__(self):
        return f'[{", ".join([str(elem) for elem in self.elements])}]'
        

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
    def __init__(self, parent=None):
        self.symbols = dict()
        self.parent = parent  # to keep track of the stack frame that holds all variables in the symbol table
    
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
    
    def _visit_StringNode(self, node, context):
        result = String(node.token.value).set_context(context).set_pos(node.start_pos, node.end_pos)
        return RuntimeResult().success(result)
    
    def _visit_ListNode(self, node, context):
        runtime_result = RuntimeResult()
        elements = []
        
        for element_node in node.element_nodes:
            elements.append(runtime_result.register(self.visit(element_node, context)))
            if runtime_result.error: runtime_result
            
        return runtime_result.success(List(elements).set_context(context).set_pos(node.start_pos, node.end_pos))
        
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
        value = value.copy().set_pos(node.start_pos, node.end_pos).set_context(context)
        
        return runtime_result.success(value)       
    
    def _visit_IfNode(self, node, context):
        runtime_result = RuntimeResult()
        
        for condition, expr, should_return_null in node.cases:
            condition_value = runtime_result.register(self.visit(condition, context))
            if runtime_result.error: return runtime_result
            
            if condition_value.is_true():
                expr_value = runtime_result.register(self.visit(expr, context))
                if runtime_result.error: return runtime_result
                return runtime_result.success(Number.null if should_return_null else expr_value)
        
        if node.else_case:
            expr, should_return_null = node.else_case
            else_case_value = runtime_result.register(self.visit(expr, context))
            if runtime_result.error: return runtime_result
            return runtime_result.success(Number.null if should_return_null else else_case_value)
        
        return runtime_result.success(Number.null)
    
    def _visit_ForNode(self, node, context):
        runtime_result = RuntimeResult()
        elements = []
        
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
            elements.append(runtime_result.register(self.visit(node.body_node, context)))
            if runtime_result.error: return runtime_result
        
        return runtime_result.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.start_pos, node.end_pos))
        
    def _visit_WhileNode(self, node, context):
        runtime_result = RuntimeResult()
        elements = []
        
        while True:
            condition_value = runtime_result.register(self.visit(node.condition_node, context))
            if runtime_result.error: return runtime_result

            if not condition_value.is_true(): break
            
            elements.append(runtime_result.register(self.visit(node.body_node, context)))
            if runtime_result.error: return runtime_result
        
        return runtime_result.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.start_pos, node.end_pos))
    
    def _visit_FuncDefinitionNode(self, node, context):
        runtime_result = RuntimeResult()
        
        func_name = node.func_name_token.value if node.func_name_token else None
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        body_node = node.body_node
        
        # create function
        func_value = Function(func_name, arg_names, body_node, node.should_return_null)\
            .set_pos(node.start_pos, node.end_pos).set_context(context)
            
        if node.func_name_token:
            context.symbol_table.set(func_name, func_value)
        
        return runtime_result.success(func_value)
    
    def _visit_FuncCallNode(self, node, context):
        runtime_result = RuntimeResult()
        
        args = []
        
        value_to_call = runtime_result.register(self.visit(node.node_to_call, context))
        if runtime_result.error: return runtime_result
        
        value_to_call = value_to_call.set_pos(node.start_pos, node.end_pos).set_context(context)
        
        for arg_node in node.arg_nodes:
            args.append(runtime_result.register(self.visit(arg_node, context)))
            if runtime_result.error: return runtime_result
            
        return_value = runtime_result.register(value_to_call.execute(args))
        if runtime_result.error: return runtime_result
        
        return_value = return_value.copy().set_pos(node.start_pos, node.end_pos).set_context(context)
        
        return runtime_result.success(return_value)

############################################
# RUN
############################################

# set up symbol table for global variables
global_symbol_table = SymbolTable()
global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("math_pi", Number.math_PI)
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_num", BuiltInFunction.is_number)
global_symbol_table.set("is_str", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_func", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)


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
