keywords = ['class', 'constructor', 'function', 'method', 'field',
            'static', 'var', 'int', 'char', 'boolean', 'true', 'false',
            'void', 'null', 'this', 'let', 'do', 'while', 'if', 'else', 'return']
symbols = {'(': '(', ')': ')', '{': '{', '}': '}', '[': '[', ']': ']', '.': '.', ',': ',', ';': ';', '+': '+', '-': '-',
           '*': '*', '/': '/', '&': '&amp;', '|': '|', '<': '&lt;', '>': '&gt;', '=': '=', '~': '~'}


class Tokenizing:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')
        self.fileXML = open(file_path[:-5] + 'T.xml', 'w')

    def write_file(self, kind, token):
        self.fileXML.write('<' + kind + '> ' + token + ' </' + kind + '>'+'\n')

    def next_token(self):
        char = self.file.read(1)
        if not char:
            return False
        token = char
        if char == '/':
            char = self.file.read(1)
            if char == '/':
                self.file.readline()
                return True
            elif char == '*':
                char = self.file.read(1)
                while not (char == '*' and self.file.read(1) == '/'):
                    char = self.file.read(1)
                return self.next_token()
            self.file.seek(self.file.tell() - 1)
            char = '/'
        if char.isdigit():
            char = self.file.read(1)
            while char.isdigit():
                token += char
                char = self.file.read(1)
            self.file.seek(self.file.tell()-1)
            self.write_file('integerConstant', token)
            return True
        elif char in symbols.keys():
            token = symbols[char]
            self.write_file('symbol', token)
            return True
        elif char == '"':
            token = ''
            char = self.file.read(1)
            while char != '"':
                token += char
                char = self.file.read(1)
            self.write_file("stringConstant", token)
            return True
        elif char.isalpha() or char == '_':
            char = self.file.read(1)
            cur = self.file.tell()-1
            while char.isalpha() or char.isdigit() or char == '_':
                token += char
                cur = self.file.tell()
                char = self.file.read(1)
            self.file.seek(cur)

            if token in keywords:
                self.write_file('keyword', token)
            else:
                self.write_file('identifier', token)
            return True
        return self.next_token()

    def file_to_tokens(self):
        self.fileXML.write("<tokens>\n")
        while self.next_token():
            pass
        self.fileXML.write("</tokens>\n")
