from StringWithArrows import *

DIGITS = "0123456789"
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'


symbolToTok = {
    "+": TT_PLUS,
    "-": TT_MINUS,
    "*": TT_MUL,
    "/": TT_DIV,
    "(": TT_LPAREN,
    ")": TT_RPAREN
}


class Error:
    def __init__(self, posStart, posEnd, errName, details):
        self.errName = errName
        self.details = details
        self.posStart = posStart
        self.posEnd = posEnd

    def as_string(self):
        result = f'{self.errName}: {self.details}'
        result += f' \nFile {self.posStart.fName}, line {self.posStart.ln + 1}'
        result += '\n\n' + string_with_arrows(self.posStart.fText, self.posStart, self.posEnd)
        return result


class IllegalCharError(Error):
    def __init__(self, posStart, posEnd, details):
        super().__init__(posStart, posStart, 'Illegal Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, posStart, posEnd, details=''):
        super().__init__(posStart, posStart, 'Invalid Syntax', details)


class Position:
    def __init__(self, idx, ln, col, fName, fText):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fName = fName
        self.fText = fText

    def advance(self, curChar=None):
        self.idx += 1
        self.col += 1

        if curChar == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fName, self.fText)


class Token:
    def __init__(self, type_, value=None, posStart=None, posEnd=None):
        self.type = type_
        self.value = value

        if posStart: 
            self.posStart = posStart.copy()
            self.posEnd = posStart.copy()
            self.posEnd.advance()

        if posEnd: 
            self.posEnd = posEnd


    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'

        return f'{self.type}'


class Lexer:
    def __init__(self, fName, text):
        self.fName = fName
        self.text = text
        self.pos = Position(-1, 0, -1, fName, text)
        self.curChar = None
        self.advance()

    def advance(self):
        self.pos.advance(self.curChar)
        self.curChar = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

    def makeTokens(self):
        tokens = []

        while self.curChar != None:
            if self.curChar in ' \t':
                self.advance()
            elif self.curChar in DIGITS:
                tokens.append(self.makeNumber())
            elif self.curChar in '+-*/()':
                tokens.append(Token(symbolToTok[self.curChar], posStart=self.pos))
                self.advance()
            else:
                posStart = self.pos.copy()
                char = self.curChar
                self.advance()
                return [], IllegalCharError(posStart, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, posStart=self.pos))

        return tokens, None

    def makeNumber(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.curChar != None and self.curChar in DIGITS + '.':
            if self.curChar == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.curChar
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.right = right
        self.operator = operator

    def __repr__(self):
	    return f'({self.left}, {self.operator}, {self.right})'

class UnaryOpNode: 
    def __init__(self, operator, node):
        self.operator = operator
        self.node = node

    def __repr__(self): 
        return f'({self.operator}, {self.node})'

class ParseResult:
    def __init__(self): 
        self.error = None
        self.node = None 

    def register(self, res):
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


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokIdx = -1
        self.advance()

    def advance(self):
        self.tokIdx += 1
        if self.tokIdx < len(self.tokens):
	        self.current_tok = self.tokens[self.tokIdx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF: 
            return res.failure(InvalidSyntaxError(
                self.current_tok.posStart, self.current_tok.posEnd, 
                "Expected '+', '-', '*', '*' or '/'"
            ))
        return res

    def test(self, s1: str, s2: str):
        if len(s1) == len(s2): print("Equal")
        else: print("stupid")

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS): 
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT): 
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_LPAREN: 
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            #print(self.current_tok)
            #print(TT_RPAREN)
            #self.test(self.current_tok, TT_RPAREN)
            if self.current_tok.type == TT_RPAREN: 
                print("In r paren shit")
                res.register(self.advance())
                return res.success(expr)
            else: 
                print(self.current_tok)
                return res.failure(InvalidSyntaxError(self.current_tok.posStart, self.current_tok.posEnd, "Expected ')'"))

        return res.failure(InvalidSyntaxError(
            tok.posStart, tok.posEnd, "Expected int or float"
        ))

    def term(self): 
        return self.binOp(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.binOp(self.term, (TT_PLUS, TT_MINUS))

    def binOp(self, func, ops): 
        res = ParseResult()
        left = res.register(func())

        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)



        

def run(fName, text):
    lexer = Lexer(fName, text)
    tokens, err = lexer.makeTokens()
    if err: return None, err


    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error
