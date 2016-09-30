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

        stack = []
        for line in template_str.split('\n'):
            line = line.strip()
            tokens = token_matcher.split(line)
            if tokens[0].startswith('{{'):
                code.add_line("")
            elif tokens[0].startswith('{% end'):
                tmp = []
                tmp.append(stack.pop())
            elif tokens[0].startswith('{%'):
                tmp = "for %s in %s:" % (tokens[1].strip(), tokens[2].strip())
                stack.append(tmp)
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

