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
