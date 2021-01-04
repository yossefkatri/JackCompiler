
ops = {'+': 'add', '-': 'sub', '*': "call Math.multiply 2", '/': "call Math.divide 2", '&amp;': 'and', '|': 'or',
       '&lt;': 'lt', '&gt;': 'gt', '=': 'eq'}
variable = {'field': 'this', 'var': 'local', 'static': 'static', 'argument': 'argument'}


class Parser:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')
        self.tab = 0
        self.method_scope = []
        self.class_scope = []
        self.class_name = ''
        self.counters = {'static': 0, 'field': 0, 'argument': 0, 'var': 0}
        self.if_index = -1
        self.while_index = -1
        if self.file.readline() != "<tokens>\n":
            return False
        self.fileXML = open(file_path[:-5] + '.xml', 'w')
        self.fileVM = open(file_path[:-5] + '.vm', 'w')

    def getNextToken(self):
        token = self.file.readline()
        if token == '</tokens>\n':
            return 'EOF', 'EOF'
        type = token.split()[0][1:-1]
        value = token.split(type)[1][2:-3]
        self.current = type, value
    # finished
    def write_terminal(self, token=False):
        if not token:
            token = self.current
        self.fileXML.write(self.tab * '  ' + '<' + token[0] + '> ' + token[1] + ' </' + token[0] + '>' + '\n')
        #print(self.tab * '  ' + '<' + token[0] + '> ' + token[1] + ' </' + token[0] + '>' + '\n')
    # finished
    def write_non_terminal(self, kind, open):
        if open is True:
            self.fileXML.write(self.tab * '  ' + '<' + kind + '>\n')
            self.tab += 1
        # print(self.tab * '  ' + '<' + kind + '>\n')
        else:
            self.tab -= 1
            self.fileXML.write(self.tab * '  ' + '</' + kind + '>' + '\n')
            #print(self.tab * '  ' + '</' + kind + '>' + '\n')
    # finished
    def parse_class(self):
        self.write_non_terminal('class', True)
        self.getNextToken()
        self.write_terminal()  # 'class'
        self.getNextToken()
        self.write_terminal()  # className
        self.class_name = self.current[1]
        self.getNextToken()
        self.write_terminal()  # '{'
        self.getNextToken()
        while self.current[1] in ['field', 'static']:
            self.parse_classVarDec()
        while self.current[1] in ['constructor', 'function', 'method']:
            self.parse_SubDec()
        self.write_terminal()  # '}'
        self.write_non_terminal('class', False)
        self.getNextToken()
        if self.current[1] == 'EOF':
            return True
        return False
    # finished
    def parse_classVarDec(self):
        self.write_non_terminal('classVarDec', True)
        row = [0, 0, 0, 0]
        self.write_terminal()  # 'static' or 'field'
        row[2] = self.current[1]
        row[3] = self.counters[self.current[1]]
        self.counters[self.current[1]] += 1
        self.getNextToken()
        self.write_terminal()  # type
        row[1] = self.current[1]
        self.getNextToken()
        self.write_terminal()  # varName
        row[0] = self.current[1]
        self.getNextToken()
        self.class_scope.append(row[:])
        while self.current[1] == ',':
            self.write_terminal()  # ','
            self.getNextToken()
            self.write_terminal()  # varName
            row[0] = self.current[1]
            row[3] = self.counters[row[2]]
            self.getNextToken()
            self.counters[row[2]] += 1
            self.class_scope.append(row[:])
        self.write_terminal()  # ';'
        self.getNextToken()
        self.write_non_terminal('classVarDec', False)
    # finished
    def parse_SubDec(self):
        self.method_scope = []
        self.write_non_terminal('subroutineDec', True)
        self.write_terminal()  # write constructor, function, method
        kind = self.current[1]
        if self.current[1] == 'method':
            row = ['this', self.class_name, 'argument', 0]
            self.method_scope.append(row[:])
            self.counters['argument'] = 1
            self.counters['var'] = 0
        else:
            self.counters['argument'] = 0
            self.counters['var'] = 0
        self.getNextToken()
        self.write_terminal()  # void, type
        self.getNextToken()
        subroutineName = self.current[1]
        self.write_terminal()  # subroutineName
        self.getNextToken()
        self.write_terminal()  # '('
        self.getNextToken()
        self.parse_parameterList()
        self.write_terminal()
        self.getNextToken()
        n = self.parse_subroutineBody()
        self.fileVM.writelines("function "+self.class_name+'.'+subroutineName+' '+str(n)+'\n')
        if kind == 'constructor':
            n = len(list(filter(lambda sublist: sublist[2] == 'field', self.class_scope)))
            self.fileVM.writelines("push constant " + str(n) + '\n')
            self.fileVM.writelines("call Memory.alloc 1\n")
            self.fileVM.writelines("pop pointer 0\n")
        elif kind == 'method':
            self.fileVM.writelines("push argument 0\n")
            self.fileVM.writelines("pop pointer 0\n")
        self.parse_subroutineBody(False)
        self.write_non_terminal('subroutineDec', False)
    # finished
    def parse_parameterList(self):
        self.write_non_terminal("parameterList", True)
        row = [0, 0, 'argument', 0]
        if self.current[1] != ')':
            self.write_terminal()  # type
            row[1] = self.current[1]
            self.getNextToken()
            self.write_terminal()  # varName
            row[0] = self.current[1]
            row[3] = self.counters['argument']
            self.counters['argument'] += 1
            self.method_scope.append(row[:])
            self.getNextToken()
            while self.current[1] == ',':
                self.write_terminal()  # ','
                self.getNextToken()
                self.write_terminal()  # type
                row[1] = self.current[1]
                self.getNextToken()
                self.write_terminal()  # varName
                row[0] = self.current[1]
                row[3] = self.counters['argument']
                self.counters['argument'] += 1
                self.method_scope.append(row[:])
                self.getNextToken()
        self.write_non_terminal("parameterList", False)
    # finished
    def parse_subroutineBody(self, flag=True):
        if flag:
            tmp = 0
            self.write_non_terminal('subroutineBody', True)
            self.write_terminal()  # '{'
            self.getNextToken()
            while self.current[1] == 'var':
                tmp += self.parse_varDec()
            return tmp
        if not flag:
            self.parse_statements()
            self.write_terminal()  # '}'
            self.getNextToken()
            self.write_non_terminal('subroutineBody', False)
    # finished
    def parse_statements(self):
        self.write_non_terminal('statements', True)
        while self.current[1] != '}':
            self.parse_statement()
        self.write_non_terminal('statements', False)
    # finished
    def parse_statement(self):
        if self.current[1] == 'let':
            self.parse_letStatement()
        elif self.current[1] == 'if':
            self.parse_ifStatement()
        elif self.current[1] == 'while':
            self.parse_whileStatement()
        elif self.current[1] == 'do':
            self.parse_doStatement()
        elif self.current[1] == 'return':
            self.parse_returnStatement()
    # finished
    def parse_letStatement(self):
        self.write_non_terminal('letStatement', True)
        self.write_terminal()  # 'let'
        self.getNextToken()
        tmp = self.current[1]
        self.write_terminal()  # varName
        self.getNextToken()
        i = [sublist[0] for sublist in self.class_scope + self.method_scope].index(tmp)
        kind = variable[(self.class_scope + self.method_scope)[i][2]]
        hasthag = str((self.class_scope + self.method_scope)[i][3])
        tmp1 = self.current[1]
        if self.current[1] == '[':
            self.write_terminal()  # '['
            self.getNextToken()
            self.parse_expression()
            self.fileVM.writelines('push ' + kind + ' ' + hasthag + '\n')
            self.fileVM.writelines('add\n')
            self.write_terminal()  # ']'
            self.getNextToken()
            kind = 'that'
            hasthag = '0'

        self.write_terminal()  # '='
        self.getNextToken()
        self.parse_expression()
        if tmp1 == '[':
            self.fileVM.writelines("pop temp 0\n")
            self.fileVM.writelines("pop pointer 1\n")
            self.fileVM.writelines("push temp 0\n")
        self.fileVM.writelines('pop ' + kind + ' ' + str(hasthag) + '\n')
        self.write_terminal()  # ';'
        self.getNextToken()
        self.write_non_terminal('letStatement', False)
    # finished
    def parse_ifStatement(self):
        self.write_non_terminal('ifStatement', True)
        self.if_index += 1
        tmp = self.if_index
        self.write_terminal()  # 'if'
        self.getNextToken()
        self.write_terminal()  # '('
        self.getNextToken()
        self.parse_expression()
        self.fileVM.writelines("if-goto IF_TRUE" + str(tmp)+'\n')
        self.fileVM.writelines("goto IF_FALSE" + str(tmp)+'\n')
        self.fileVM.writelines("label IF_TRUE" + str(tmp)+'\n')
        self.write_terminal()  # ')'
        self.getNextToken()
        self.write_terminal()  # '{'
        self.getNextToken()
        self.parse_statements()
        self.write_terminal()  # '}'
        self.getNextToken()
        if self.current[1] == 'else':
            self.fileVM.writelines('goto IF_END' + str(tmp) + '\n')
            self.fileVM.writelines("label IF_FALSE" + str(tmp) + '\n')
            self.write_terminal()  # 'else'
            self.getNextToken()
            self.write_terminal()  # '{'
            self.getNextToken()
            self.parse_statements()
            self.write_terminal()  # '}'
            self.getNextToken()
            self.fileVM.writelines("label IF_END" + str(tmp)+'\n')
        else:
            self.fileVM.writelines("label IF_FALSE" + str(tmp) + '\n')
        self.write_non_terminal('ifStatement', False)
    # finished
    def parse_whileStatement(self):
        self.while_index += 1
        self.write_non_terminal('whileStatement', True)
        self.fileVM.writelines("label WHILE_EXP" + str(self.while_index)+'\n')
        self.write_terminal()  # 'while'
        self.getNextToken()
        self.write_terminal()  # '('
        self.getNextToken()
        self.parse_expression()
        self.fileVM.writelines("not"+'\n')
        self.fileVM.writelines("if-goto WHILE_END" + str(self.while_index)+'\n')
        self.write_terminal()  # ')'
        self.getNextToken()
        tmp = self.while_index
        self.write_terminal()  # '{'
        self.getNextToken()
        self.parse_statements()
        self.fileVM.writelines("goto WHILE_EXP" + str(tmp)+'\n')
        self.write_terminal()  # '}'
        self.fileVM.writelines("label WHILE_END" + str(tmp)+'\n')
        self.getNextToken()
        self.write_non_terminal('whileStatement', False)
    # finished
    def parse_doStatement(self):
        self.write_non_terminal('doStatement', True)
        self.write_terminal()  # 'do'
        self.getNextToken()
        self.parse_subroutineCall()
        self.write_terminal()  # ';'
        self.fileVM.writelines("pop temp 0"+'\n')
        self.getNextToken()
        self.write_non_terminal('doStatement', False)
    # finished
    def parse_returnStatement(self):
        self.write_non_terminal('returnStatement', True)
        self.write_terminal()  # 'return'
        self.getNextToken()
        if self.current[1] != ';':
            self.parse_expression()
        else:
            self.fileVM.writelines('push constant 0'+'\n')
        self.write_terminal()
        self.getNextToken()
        self.fileVM.writelines('return'+'\n')
        self.write_non_terminal('returnStatement', False)
    # finished
    def parse_expression(self):
        self.write_non_terminal('expression', True)
        self.parse_term()
        while self.current[1] in ['+', '-', '*', '/', '&amp;', '|', '', '&lt;', '&gt;', '=']:
            self.write_terminal()  # op
            op_temp = self.current[1]
            self.getNextToken()
            self.parse_term()
            self.fileVM.writelines(ops[op_temp]+'\n')
        self.write_non_terminal('expression', False)
    # finished

    def parse_subroutineCall(self, ll1=False, id=''):
        n = 0
        func_name = ''
        class_name = ''
        if not ll1:
            self.write_terminal()  # id
            id += self.current[1]
            self.getNextToken()
        if self.current[1] == '.':
            self.write_terminal()  # '.'
            self.getNextToken()
            self.write_terminal()  # id
            func_name = self.current[1]
            self.getNextToken()
        elif self.current[1] == '(':
            func_name = id
            class_name = self.class_name
            id = ''
        if id == '':
            self.fileVM.writelines("push pointer 0\n")
            n += 1
        elif id in [sublist[0] for sublist in self.method_scope]:
            i = [sublist[0] for sublist in self.method_scope].index(id)
            class_name = self.method_scope[i][1]
            self.fileVM.writelines("push " + variable[self.method_scope[i][2]]+' ' + str(self.method_scope[i][3])+'\n')
            n += 1
        elif id in [sublist[0] for sublist in self.class_scope]:
            i = [sublist[0] for sublist in self.class_scope].index(id)
            class_name = self.class_scope[i][1]
            self.fileVM.writelines("push " + variable[self.class_scope[i][2]]+' ' + str(self.class_scope[i][3])+'\n')
            n += 1
        else:
            class_name = id
        self.write_terminal()  # '('
        self.getNextToken()
        n += self.parse_expressionList()
        self.write_terminal()  # ')'
        full_name = class_name + '.' + func_name
        self.fileVM.writelines("call " + full_name + ' ' + str(n)+'\n')
        self.getNextToken()
    # finished
    def parse_term(self):
        self.write_non_terminal('term', True)
        if self.current[0] in ['integerConstant', 'stringConstant'] or self.current[1] in ['this', 'null', 'true','false']:
            if self.current[1] == 'true':
                self.fileVM.writelines('push constant 0'+'\n')
                self.fileVM.writelines('not'+'\n')
            elif self.current[1] in ['false', 'null']:
                self.fileVM.writelines('push constant 0' + '\n')
            elif self.current[1] == 'this':
                self.fileVM.writelines('push pointer 0' + '\n')
            if self.current[0] == 'integerConstant':
                self.fileVM.writelines('push constant '+self.current[1]+'\n')
            if self.current[0] == 'stringConstant':
                self.fileVM.writelines('push constant '+str(len(self.current[1]))+'\n')
                self.fileVM.writelines('call String.new 1'+'\n')
                for i in range(len(self.current[1])):
                    tmp = ord(self.current[1][i])
                    self.fileVM.writelines('push constant ' + str(tmp)+'\n')
                    self.fileVM.writelines('call String.appendChar 2' + '\n')
            self.write_terminal()  # (integer|string|keyword|varName)Constant
            self.getNextToken()
        elif self.current[1] == '(':
            self.write_terminal()  # '('
            self.getNextToken()
            self.parse_expression()
            self.write_terminal()  # ')'
            self.getNextToken()
        elif self.current[1] in ['-', '~']:
            self.write_terminal()  # unaryOp
            tmp = self.current[1]
            self.getNextToken()
            self.parse_term()
            if tmp == '-':
                self.fileVM.writelines('neg'+'\n')
            else:
                self.fileVM.writelines('not'+'\n')
        elif self.current[0] == 'identifier':
            id = self.current[1]
            self.write_terminal()
            self.getNextToken()
            if self.current[1] == '[':
                self.write_terminal()  # '['
                self.getNextToken()
                self.parse_expression()
                i = [sublist[0] for sublist in self.class_scope+self.method_scope].index(id)
                kind = variable[(self.class_scope+self.method_scope)[i][2]]
                hasthag = (self.class_scope+self.method_scope)[i][3]
                self.fileVM.writelines('push ' + kind + ' ' + str(hasthag) + '\n')
                self.fileVM.writelines('add\n')
                self.fileVM.writelines('pop pointer 1\n')
                self.fileVM.writelines('push that 0\n')
                self.write_terminal()  # ']'
                self.getNextToken()
            elif self.current[1] in ['(', '.']:
                self.parse_subroutineCall(True, id)
            else:
                i = [sublist[0] for sublist in self.class_scope + self.method_scope].index(id)
                kind = variable[(self.class_scope + self.method_scope)[i][2]]
                hasthag = (self.class_scope + self.method_scope)[i][3]
                self.fileVM.writelines('push ' + kind + ' ' + str(hasthag) + '\n')
        self.write_non_terminal('term', False)
    # finished
    def parse_expressionList(self):
        self.write_non_terminal('expressionList', True)
        tmp = 0
        if self.current[1] != ')':
            self.parse_expression()
            tmp += 1
        while self.current[1] == ',':
            self.write_terminal()  # ','
            self.getNextToken()
            self.parse_expression()
            tmp += 1
        self.write_non_terminal('expressionList', False)
        return tmp
    # finished

    def parse_varDec(self):
        n = 1
        self.write_non_terminal('varDec', True)
        row = [0, 0, 'var', 0]
        self.write_terminal()  # 'var'
        self.getNextToken()
        self.write_terminal()  # type
        row[1] = self.current[1]
        self.getNextToken()
        self.write_terminal()  # varName
        row[0] = self.current[1]
        self.getNextToken()
        row[3] = self.counters['var']
        self.counters['var'] += 1
        self.method_scope.append(row[:])
        while self.current[1] == ',':
            n += 1
            self.write_terminal()  # ','
            self.getNextToken()
            self.write_terminal()  # varName
            row[0] = self.current[1]
            row[3] = self.counters['var']
            self.counters['var'] += 1
            self.method_scope.append(row[:])
            self.getNextToken()

        self.write_terminal()  # ';'
        self.getNextToken()
        self.write_non_terminal('varDec', False)
        return n
    # finished