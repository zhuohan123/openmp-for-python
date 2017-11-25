import ast
import parseprint
import sys

if len(sys.argv)!=2:
    raise ValueError('File name needed!')

file = open(sys.argv[1])
original_code=file.read()

class variable_checker(ast.NodeVisitor):
    def visit(self, node):
        ast.NodeVisitor.visit(self,node)

    def visit_FunctionDef(self, node):
        print 'function begin', node.name, node.lineno
        self.generic_visit(node)

        lastBody = node.body[-1]
        while 'body' in lastBody._attributes:
            lastBody = lastBody.body[-1]
        lastLine = lastBody.lineno
        print 'function end', node.name, lastLine+1

    def visit_arguments(self, node):
        self.generic_visit(node)
        if node.vararg!=None:
            print 'vararg',node.vararg
        if node.kwarg != None:
            print 'kwarg', node.kwarg

    def visit_Global(self, node):
        for name in node.names:
            print 'global',name
        self.generic_visit(node)

    def visit_Name(self, node):
        var_state = 'unknown'
        if isinstance(node.ctx, ast.Store):
            var_state = 'store'
        elif isinstance(node.ctx, ast.Load):
            var_state = 'load'
        elif isinstance(node.ctx, ast.Del):
            var_state = 'del'
        elif isinstance(node.ctx, ast.Param):
            var_state = 'param'
        if var_state == 'param':
            print 'arg',node.id
        else:
            print 'variable',node.lineno, node.col_offset, node.id, var_state
        self.generic_visit(node)

    def visit_comprehension(self, node):
        print 'comprehension start'
        self.generic_visit(node)
        print 'comprehension end'

    def visit_Lambda(self, node):
        print 'lambda start'
        self.generic_visit(node)
        print 'lambda end'

    def visit_For(self, node):
        print 'for begin', node.lineno
        self.generic_visit(node)
        lastBody = node.body[-1]
        while 'body' in lastBody._attributes:
            lastBody = lastBody.body[-1]
        lastLine = lastBody.lineno
        print 'for end', lastLine+1

tree = ast.parse(original_code)

variable_checker().visit(tree)

#parseprint.parseprint(tree, include_attributes=True)
