
import re

def test_tokenize(text):
    token_matcher = re.compile(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})")
    print token_matcher.split(text)

if __name__ == '__main__':
    test_tokenize("<p> hello world</p>")
    test_tokenize("<p> hello, {{ name }}</p>\n{% for product in products %}\n<p>product</p>\n{% end %}")
