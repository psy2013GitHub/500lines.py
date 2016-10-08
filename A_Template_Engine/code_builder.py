
class CodeBuilder:

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def __str__(self):
        return ''.join([str(_) for _ in self.code])

    def indent(self):
        self.indent_level += 1

    def unindent(self):
        self.indent_level -= 1

    def add_line(self, line):
        self.code.extend(['    ' * self.indent_level, line, '\n'])

    def add_section(self):
        sub_code = CodeBuilder(self.indent_level)
        self.code.append(sub_code)
        return sub_code


if __name__ == '__main__':
    inst = CodeBuilder()
    inst.add_line("def hello_world():")
    inst.indent()
    inst.add_line("print \"hello, world\"")
