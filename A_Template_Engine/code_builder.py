
class CodeBuilder:

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def indent(self):
        self.indent_level += 1

    def unindent(self):
        self.indent_level -= 1

    def add_line(self, line):
        self.code.append(['    ' * self.indent_level, line, '\n'])

    def add_section(self):
        pass

    def flush_output(self):
        out = []
        return ''.join([' '.join(_) for _ in self.code])


if __name__ == '__main__':
    inst = CodeBuilder()
    inst.add_line("def hello_world():")
    inst.indent()
    inst.add_line("print \"hello, world\"")
    print inst.flush_output()