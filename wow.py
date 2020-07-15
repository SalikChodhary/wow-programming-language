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

class RTError(Error):
    def __init__(self, posStart, posEnd, details, context):
        super().__init__(posStart, posStart, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generateTraceback()
        result += f'{self.errName}: {self.details}'
        result += '\n\n' + string_with_arrows(self.posStart.fText, self.posStart, self.posEnd)
        return result

    def generateTraceback(self):
        result = ''
        pos = self.posStart
        context = self.context

        while context: 
            result = f'File {pos.fName}, line {str(pos.ln + 1)}. in {context.displayName}' + '\n' + result
            pos = context.parentEntryPos
            context = context.parent

        return 'Traceback (most recent call last): \n' + result
        


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
        self.posStart = self.tok.posStart
        self.posEnd = self.tok.posEnd

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.right = right
        self.operator = operator

        self.posStart = self.left.posStart
        self.posEnd = self.right.posEnd

    def __repr__(self):
	    return f'({self.left}, {self.operator}, {self.right})'

class UnaryOpNode: 
    def __init__(self, operator, node):
        self.operator = operator
        self.node = node

        self.posStart = self.operator.posStart
        self.posEnd = node.posEnd

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

class Number:
    def __init__(self, value): 
        self.value = value
        self.setPos()
        self.setContext()

    def setContext(self, context=None):
        self.context = context
        return self
    
    def setPos(self, posStart=None, posEnd=None): 
        self.posStart = posStart
        self.posEnd = posEnd
        return self

    def addedTo(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).setContext(self.context), None
    
    def subtractedBy(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).setContext(self.context), None

    def multipliedBy(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).setContext(self.context), None

    def dividedBy(self, other):
        if isinstance(other, Number): 
            if other.value == 0: 
                return None, RTError(
                    other.posStart, other.posEnd, 'Division by zero', 
                    self.context
                )
            return Number(self.value / other.value).setContext(self.context), None
    
    def __repr__(self): 
        return str(self.value)

class RunTimeResult:
    def __init__(self): 
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value

    def success(self, value): 
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

class Context: 
    def __init__(self, displayName, parent=None, parentEntryPos=None):
        self.displayName = displayName
        self.parent = parent
        self.parentEntryPos = parentEntryPos


class Interpreter: 
    def visit(self, node, context): 
        #different method depending on tyoe of node
        methodName = f'visit{type(node).__name__}'
        method = getattr(self, methodName, self.noVisitMethod)
        return method(node, context)
    def noVisitMethod(self, node, context):
        
        raise Exception(f'No visit method defined')

    def visitNumberNode(self, node, context):
        newNumber = Number(node.tok.value)
        newNumber.setContext(context)
        newNumber.setPos(node.posStart, node.posEnd)
        return RunTimeResult().success(newNumber)

    def visitBinOpNode(self, node, context):
        #print("Found binary operator node")
        res = RunTimeResult()
        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))

        if node.operator.type == TT_PLUS: 
            result, error = left.addedTo(right)
        elif node.operator.type == TT_MINUS: 
            result, error = left.subtractedBy(right)
        elif node.operator.type == TT_MUL: 
            result, error = left.multipliedBy(right)
        elif node.operator.type == TT_DIV: 
            result, error = left.dividedBy(right)

        if error: 
            return res.failure(error)
        else:
            return res.success(result.setPos(node.posStart, node.posEnd))

    def visitUnaryOpNode(self, node, context):
       # print("unary op node")
        res = RunTimeResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.operator.type == TT_MINUS: 
            number, error = number.multipliedBy(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.setPos(node.posStart, node.posEnd))

def run(fName, text):
    lexer = Lexer(fName, text)
    tokens, err = lexer.makeTokens()
    if err: return None, err


    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
