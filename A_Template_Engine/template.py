#-*- encoding: utf8 -*-

import re
from code_builder import CodeBuilder

global token_matcher
token_matcher = re.compile(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})")

class Template:

    def __init__(self, template_str, *context_dict_args):
        '''
            parse template_str and build python-code-str
        :context_dict_args: args
        :param template_str:
        :return:
        '''
        context = dict()
        for arg in context_dict_args:
            context.update(arg)
        self.context = context

        self.loop_vars = set()
        self.all_vars = set()

        global token_matcher
        code = CodeBuilder()
        # head
        code.add_line("def render_template(context, do_dots):")
        code.indent()
        code.add_line("res = []")
        code.add_line("append_res = res.append")
        code.add_line("extend_res = res.extend")
        code.add_line("to_str=str")
        var_code = code.add_section()
        # code.add_line("return res")

        buffer = []
        def flush_buffer():
            print 'code.indent_level:', code.indent_level, ' buffer:', buffer
            if len(buffer) > 1:
                code.add_line("extend_res([%s,])" % ','.join(buffer))
            elif len(buffer)==1:
                code.add_line("append_res(%s)" % buffer[0]) #repr(buffer[0]))
            del buffer[:]

        # template_str parser
        control_stack = [] # control loop
        for token in [_.strip() for _ in token_matcher.split(template_str) if _]:
            print 'token:', token
            if token.startswith('{% end'):
                flush_buffer() # caution
                end_sgn = token.split()[1][3:] # fixme
                if not control_stack:
                    raise ValueError, str(token) + '\t' + str(control_stack)
                start_sgn = control_stack.pop()
                if end_sgn != start_sgn:
                    raise ValueError, ','.join([str(control_stack), str(start_sgn), str(end_sgn)])
                code.unindent()

            elif token.startswith('{%'):
                flush_buffer()
                tmp = token.split()
                if tmp[1]=='for':
                    control_stack.append('for')
                    assert tmp[3]=='in' and len(tmp)==6, tmp
                    iter_var, loop_var = tmp[2].strip(), self.get_var(tmp[4].strip())
                    self.add_var(iter_var, self.loop_vars)
                    tmp = "for c_%s in %s:" % (iter_var, loop_var)
                    code.add_line(tmp)
                    print 'code.indent_level 1:', code.indent_level
                    code.indent()
                    print 'code.indent_level 2:', code.indent_level

            elif token.startswith('{#'): # 注释
                continue

            else:
                if token.startswith('{{'):
                    buffer.append('%s' % self.get_var(token[2:-2]))
                else:
                    buffer.append('%s' % repr(token))

        print 'final flush_buffer:'
        flush_buffer()

        for var in self.all_vars - self.loop_vars:
            var_code.add_line('c_%s=context[%s]' % (var, repr(var)))

        code.add_line('return res')

        self.code = str(code)
        print '\n\n', self.code #code.flush_output()
        print '\n\nall_vars:', str(self.all_vars)
        print '\n\nloop_vars:', str(self.loop_vars)

    def get_var(self, var_str):
        '''
            get value from val_str
        :param var_str:
        :return:
        '''
        code = ''
        var_str = var_str.strip()
        if '|' in var_str:
            tmp = var_str.split('|')
            var = tmp[0]
            code = self.get_var(var)
            for f in tmp[1:]:
                code = 'c_%s(%s)' % (f, code)
                self.add_var(f, self.all_vars)
        elif '.' in var_str:
            tmp = var_str.split('.')
            var = tmp[0]
            code = 'do_dots(c_%s, *%s)' % (tmp[0], tmp[1:])
            self.add_var(var, self.all_vars)
        else:
            var = var_str
            code = 'c_%s' % var_str
            self.add_var(var, self.all_vars)
        return code

    def add_var(self, var, target_set):
        '''
            add value to a val_set
        :param var:
        :param target_set:
        :return:
        '''
        target_set.add(var)

    def do_dots(self, var, *fields):
        '''
            惰性求值
        :param var:
        :param field:
        :return:
        '''
        assert not(var is None)
        for field in fields:
            print 'do_dots:', str(var), field
            # field = repr(field)
            try:
                var = getattr(var, field)
            except AttributeError, e:
                var = var[field]
            if callable(var):
                var = var() # fixme, only non-arg function available now
        return var

    def render(self, context):
        global_namespaces = {}
        exec(self.code, global_namespaces)
        render_template = global_namespaces['render_template']
        return render_template(context, self.do_dots)

def testReSplit():
    def split(text):
        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text.strip())
        return [_ for _ in tokens if _]

    def test(text, expected_tokens):
        tokens = split(text)
        assert tokens and len(tokens)==len(expected_tokens) and (False not in [tokens[i]==expected_tokens[i] for i in range(len(tokens))])

    print split("{% for product in product_list %}")

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

    # testReSplit()
    template = Template(html)
    print 'rendered text'
    print ''.join(template.render({'user_name':'lilian', 'product_list':[{'name':'durex', 'price':20, },], 'format_price':lambda x:'%f'%x}))

