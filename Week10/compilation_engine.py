from token_types import (KEYWORD, INTEGER, STRING, SYMBOL, IDENTIFIER)

indent = 0
token_stack = []


def _write(file, next_str):
    file.write('{}{}\n'.format(indent * ' ', next_str))


def _write_token(file, token):
    token_type, token_val = token
    _write(file, '<{}> {} </{}>'.format(token_type, token_val, token_type))


def _modify_indent(val):
    global indent

    indent += val


def _peek_stack_head(token_gen):
    if len(token_stack) == 0:
        _push(token_stack, token_gen.next())
    return token_stack[-1]


def _push(stack, token):
    stack.append(token)


def _pop(stack):
    return stack.pop()


def _compile_class(file, token_gen):
    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'class')
    _write(file, '<class>')
    _modify_indent(2)

    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '{')
    _write_token(file, _pop(token_stack))

    _compile_class_var_dec(file, token_gen)
    _compile_subroutine(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '}')
    _write_token(file, _pop(token_stack))
    _modify_indent(-2)
    _write(file, '</class>')


def _compile_class_var_dec(file, token_gen):
    class_var_dec_tokens = [(KEYWORD, 'static'), (KEYWORD, 'field')]
    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) not in class_var_dec_tokens:
        return

    _write(file, '<classVarDec>')
    _modify_indent(2)

    _write_token(file, _pop(token_stack))

    _compile_type_name(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) == (SYMBOL, ','):

        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        _write_token(file, _pop(token_stack))
        token_type, token_val = _peek_stack_head(token_gen)

    assert (token_type, token_val) == (SYMBOL, ';')
    _write_token(file, _pop(token_stack))
    _modify_indent(-2)
    _write(file, '</classVarDec>')

    _compile_class_var_dec(file, token_gen)


def _compile_subroutine(file, token_gen):
    subroutine_dec_tokens = [(KEYWORD, 'constructor'),
                             (KEYWORD, 'function'),
                             (KEYWORD, 'method')]

    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) in subroutine_dec_tokens:

        _write(file, '<subroutineDec>')
        _modify_indent(2)
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type in [IDENTIFIER, KEYWORD]
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '(')
        _write_token(file, _pop(token_stack))

        _compile_parameter_list(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, ')')
        _write_token(file, _pop(token_stack))

        _write(file, '<subroutineBody>')
        _modify_indent(2)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '{')
        _write_token(file, _pop(token_stack))

        _compile_var_dec(file, token_gen)
        _compile_statements(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '}')
        _write_token(file, _pop(token_stack))

        _modify_indent(-2)
        _write(file, '</subroutineBody>')

        _modify_indent(-2)
        _write(file, '</subroutineDec>')
        token_type, token_val = _peek_stack_head(token_gen)

    return


def _compile_type_name(file, token_gen):
    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type in [IDENTIFIER, KEYWORD]
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    _write_token(file, _pop(token_stack))


def _compile_parameter_list(file, token_gen):
    _write(file, '<parameterList>')
    _modify_indent(2)
    token_type, token_val = _peek_stack_head(token_gen)
    if token_type in [IDENTIFIER, KEYWORD]:
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        while (token_type, token_val) == (SYMBOL, ','):
            _write_token(file, _pop(token_stack))
            _compile_type_name(file, token_gen)
            token_type, token_val = _peek_stack_head(token_gen)

    _modify_indent(-2)
    _write(file, '</parameterList>')
    return


def _compile_var_dec(file, token_gen):
    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) != (KEYWORD, 'var'):
        return

    _write(file, '<varDec>')
    _modify_indent(2)
    _write_token(file, _pop(token_stack))

    _compile_type_name(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) == (SYMBOL, ','):
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)

    assert (token_type, token_val) == (SYMBOL, ';')
    _write_token(file, _pop(token_stack))
    _modify_indent(-2)
    _write(file, '</varDec>')
    _compile_var_dec(file, token_gen)
    return


def _compile_statements(file, token_gen):
    _write(file, '<statements>')
    _modify_indent(2)

    _statement_tokens = [(KEYWORD, 'let'),
                         (KEYWORD, 'if'),
                         (KEYWORD, 'while'),
                         (KEYWORD, 'do'),
                         (KEYWORD, 'return')]

    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) in _statement_tokens:
        {
            'let': lambda: _compile_let(file, token_gen),
            'do': lambda: _compile_do(file, token_gen),
            'while': lambda: _compile_while(file, token_gen),
            'if': lambda: _compile_if(file, token_gen),
            'return': lambda: _compile_return(file, token_gen)
        }[token_val]()
        token_type, token_val = _peek_stack_head(token_gen)

    _modify_indent(-2)
    _write(file, '</statements>')
    return


def _compile_let(file, token_gen):
    _write(file, '<letStatement>')
    _modify_indent(2)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'let')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) == (SYMBOL, '['):

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '[')
        _write_token(file, _pop(token_stack))

        _compile_expression(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, ']')
        _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '=')
    _write_token(file, _pop(token_stack))

    _compile_expression(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ';')
    _write_token(file, _pop(token_stack))

    _modify_indent(-2)
    _write(file, '</letStatement>')
    return


def _compile_subroutine_call(file, token_gen):
    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) == (SYMBOL, '.'):
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '(')
    _write_token(file, _pop(token_stack))

    _compile_expression_list(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ')')
    _write_token(file, _pop(token_stack))


def _compile_do(file, token_gen):

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'do')
    _write(file, '<doStatement>')
    _modify_indent(2)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'do')
    _write_token(file, _pop(token_stack))

    _compile_subroutine_call(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ';')
    _write_token(file, _pop(token_stack))

    _modify_indent(-2)
    _write(file, '</doStatement>')
    return


def _compile_if(file, token_gen):

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'if')
    _write(file, '<ifStatement>')
    _modify_indent(2)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'if')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '(')
    _write_token(file, _pop(token_stack))

    _compile_expression(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ')')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '{')
    _write_token(file, _pop(token_stack))

    _compile_statements(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '}')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) == (KEYWORD, 'else'):

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (KEYWORD, 'else')
        _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '{')
        _write_token(file, _pop(token_stack))

        _compile_statements(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '}')
        _write_token(file, _pop(token_stack))

    _modify_indent(-2)
    _write(file, '</ifStatement>')
    return


def _compile_while(file, token_gen):

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'while')
    _write(file, '<whileStatement>')
    _modify_indent(2)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'while')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '(')
    _write_token(file, _pop(token_stack))

    _compile_expression(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ')')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '{')
    _write_token(file, _pop(token_stack))

    _compile_statements(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '}')
    _write_token(file, _pop(token_stack))

    _modify_indent(-2)
    _write(file, '</whileStatement>')
    return


def _compile_return(file, token_gen):

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'return')
    _write(file, '<returnStatement>')
    _modify_indent(2)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'return')
    _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) != (SYMBOL, ';'):
        _compile_expression(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ';')
    _write_token(file, _pop(token_stack))

    _modify_indent(-2)
    _write(file, '</returnStatement>')
    return


def _compile_term(file, token_gen):

    term_keywords = ['true', 'false', 'null', 'this']

    def _is_term(token_type, token_val):
        term_types = [STRING, INTEGER, IDENTIFIER]
        term_symbols = ['(', ')', '-', '~']
        return (token_type in term_types or
                token_val in term_symbols or
                token_val in term_keywords)

    token_type, token_val = _peek_stack_head(token_gen)
    if not _is_term(token_type, token_val):
        return

    _write(file, '<term>')
    _modify_indent(2)

    if token_val in ['-', '~']:
        assert token_type == SYMBOL
        _write_token(file, _pop(token_stack))

        _compile_term(file, token_gen)

    elif token_type in [INTEGER, STRING]:
        _write_token(file, _pop(token_stack))

    elif token_val in term_keywords:
        _write_token(file, _pop(token_stack))

    elif (token_type, token_val) == (SYMBOL, '('):
        _write_token(file, _pop(token_stack))
        _compile_expression(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, ')')
        _write_token(file, _pop(token_stack))

    else:
        future_token = token_gen.next()
        token_type, token_val = future_token
        if (token_type, token_val) == (SYMBOL, '['):

            token_type, token_val = _peek_stack_head(token_gen)
            assert token_type == IDENTIFIER
            _write_token(file, _pop(token_stack))
            _write_token(file, future_token)
            _compile_expression(file, token_gen)

            token_type, token_val = _peek_stack_head(token_gen)
            assert (token_type, token_val) == (SYMBOL, ']')
            _write_token(file, _pop(token_stack))

        elif (token_type, token_val) in [(SYMBOL, '('), (SYMBOL, '.')]:
            next_token = _pop(token_stack)
            # hacky invert order of tokens in stack so that we are able to
            # compile a subroutine
            _push(token_stack, future_token)
            _push(token_stack, next_token)
            _compile_subroutine_call(file, token_gen)

        else:
            token_type, token_val = _peek_stack_head(token_gen)
            assert token_type == IDENTIFIER
            _write_token(file, _pop(token_stack))
            _push(token_stack, future_token)

    _modify_indent(-2)
    _write(file, '</term>')


def _compile_expression(file, token_gen):
    operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    _write(file, '<expression>')
    _modify_indent(2)

    _compile_term(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    if token_val in operators:
        if token_val in ['&', '<', '>']:
            escaped = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;'
            }[token_val]

            _pop(token_stack)
            _write_token(file, (SYMBOL, escaped))

        else:
            _write_token(file, _pop(token_stack))

        _compile_term(file, token_gen)

    _modify_indent(-2)
    _write(file, '</expression>')
    return


def _compile_expression_list(file, token_gen):
    _write(file, '<expressionList>')
    _modify_indent(2)

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) != (SYMBOL, ')'):
        _compile_expression(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        while (token_type, token_val) == (SYMBOL, ','):
            _write_token(file, _pop(token_stack))
            _compile_expression(file, token_gen)
            token_type, token_val = _peek_stack_head(token_gen)

    _modify_indent(-2)
    _write(file, '</expressionList>')

    return


def compile_file(file, token_gen):
    _compile_class(file, token_gen)
