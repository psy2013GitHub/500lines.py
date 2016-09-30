#-*- encoding: utf8 -*-

import re
from code_builder import CodeBuilder

global token_matcher
token_matcher = re.compile("")

class Template:


    def __init__(self, template_str):
        global token_matcher
        code = CodeBuilder()
        # head
        code.add_line("def render_template():")
        code.indent()
        code.add_line("res = []")
        code.add_line("append_res = res.append")
        code.add_line("extend_res = res.extend")
        var_code = code.add_section()
        code.add_line("return res")

        buffer = []
        def add_code(list_in):
            if len(list_in) == 0:
                buffer.append("extend_res([%s,])" % ','.join(list_in))
            else:
                buffer.append("append_res(%s)" % repr(list_in))

        control_stack = []
        for line in template_str.split('\n'):
            line = line.strip()
            tokens = [_.strip() for _ in token_matcher.split(line)]
            if tokens[0].startswith('{{'):
                add_code(tokens[0][2:-2])
            elif tokens[0].startswith('{% end'):
                end_sgn = tokens[0][3:] # fixme
                if not control_stack:
                    raise ValueError
                start_sgn = control_stack.pop()
                if end_sgn != start_sgn:
                    raise ValueError
            elif tokens[0].startswith('{%'):
                tmp = "for %s in %s:" % (tokens[1].strip(), tokens[2].strip())
                add_code(tmp)
                code.indent()
            elif tokens[0].startswith('{#'): # 注释
                continue
            else:
                code.add_line("append_res(%s)" % repr(line))


    def render(self, context):
        pass


if __name__ == '__main__':
    html = '''
        <p>Welcome, {{user_name}}!</p>
        <p>Products:</p>
        <ul>
        {% for product in product_list %}
            <li>{{ product.name }}:
                {{ product.price|format_price }}</li>
        {% endfor %}
        </ul>
    '''

    template = Template(html)

