from StringWithArrows import *

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
        
