import re
from token_types import (KEYWORD, SYMBOL, STRING, INTEGER, IDENTIFIER)

_KEYWORDS = ["class", "method", "function", "constructor", "int", "boolean",
             "char", "void", "var", "static", "field", "let", "do", "if",
             "else", "while", "return", "true", "false", "null", "this"]

_SYMBOLS = ["{", "}", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/",
            "&", "|", "<", ">", "=", "~"]


def _slice_command(line):
    stripped_line = line.strip()
    if not stripped_line:
        return ''
    is_comment = stripped_line[0] == '*' or stripped_line[0:2] in ['//', '/*']
    if is_comment:
        return ''
    without_comments = line.split('//')[0]
    identifier_regex = '\w+'
    integer_regex = '\d+'
    string_regex = '\".*\"'
    keyword_regex = ('class|method|function|constructor|int|boolean|char|void|'
                     'var|static|field|let|do|if|else|while|return|true|false|'
                     'null|this')
    symbol_regex = '{|}|\[|\]|\(|\)|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~'
    composed_regex = r'({}|{}|{}|{}|{})'.format(identifier_regex,
                                                integer_regex,
                                                string_regex,
                                                keyword_regex,
                                                symbol_regex)
    return re.finditer(composed_regex, without_comments)


def _is_keyword(word):
    return word in _KEYWORDS


def _is_symbol(symbol):
    return symbol in _SYMBOLS


def _is_string(word):
    string_regex = re.compile('^\".*\"$')
    return not not string_regex.match(word)


def _is_int(word):
    int_regex = re.compile('^\d+$')
    return not not int_regex.match(word)


def _is_identifier(word):
    identifier_regex = re.compile('^\w+$')
    return not not identifier_regex.match(word)


def _get_token(word):
    """
    Returns a tuple of token type and the actual token
    """
    if _is_keyword(word):
        return KEYWORD, word

    elif _is_symbol(word):
        return SYMBOL, word

    elif _is_string(word):
        return STRING, word.replace("\"", "")

    elif _is_int(word):
        return INTEGER, word

    elif _is_identifier(word):
        return IDENTIFIER, word

    raise Exception('Error trying to get next token {}'.format(word))

# ############ Only function to be exported ############ #


def tokenizer(file):
    """
    Generator that outputs next token
    """
    jack_file = open(file, 'r')

    for line in jack_file.readlines():
        command = _slice_command(line)
        if not command:
            continue
        for word in command:
            word = word.group().strip()
            if not word:
                continue
            yield _get_token(word.strip())
