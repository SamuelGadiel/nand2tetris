from token_types import KEYWORD, INTEGER, STRING, SYMBOL, IDENTIFIER

from symbol_table import define, kind_of, index_of, start_subroutine


from vm_writer import (
    write_arithmetic,
    write_call,
    write_function,
    write_goto,
    write_if,
    write_label,
    write_pop,
    write_push,
    write_return
)

token_stack = []
while_num = 0


def _write(file, next_str):
    file.write('{}\n'.format(next_str))


def _write_token(file, token):
    token_type, token_val = token
    _write(file, '<{}> {} </{}>'.format(token_type, token_val, token_type))


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
    # _write(file, '<class>')

    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    class_name = token_val
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '{')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    _compile_class_var_dec(file, token_gen)
    _compile_subroutine(file, token_gen, class_name)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '}')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</class>')


def _compile_class_var_dec(file, token_gen):
    class_var_dec_tokens = [(KEYWORD, 'static'), (KEYWORD, 'field')]
    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) not in class_var_dec_tokens:
        return

    # _write(file, '<classVarDec>')

    kind = token_val
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type in [IDENTIFIER, KEYWORD]
    _type = token_val
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    name = token_val
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    define(name, _type, kind)

    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) == (SYMBOL, ','):

        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        name = token_val

        define(name, _type, kind)
        _pop(token_stack)  # _write_token(file, _pop(token_stack))
        token_type, token_val = _peek_stack_head(token_gen)

    assert (token_type, token_val) == (SYMBOL, ';')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</classVarDec>')

    _compile_class_var_dec(file, token_gen)


def _compile_subroutine(file, token_gen, class_name=''):
    start_subroutine()
    subroutine_dec_tokens = [(KEYWORD, 'constructor'),
                             (KEYWORD, 'function'),
                             (KEYWORD, 'method')]

    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) in subroutine_dec_tokens:

        # _write(file, '<subroutineDec>')

        subroutine_type = token_val
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type in [IDENTIFIER, KEYWORD]
        # subroutine_return_type = token_val
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        if class_name:
            subroutine_name = '{}.{}'.format(class_name, token_val)
        else:
            subroutine_name = token_val
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '(')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        _compile_parameter_list(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, ')')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        # _write(file, '<subroutineBody>')

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '{')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        num_locals = _compile_var_dec(file, token_gen)
        if subroutine_type == 'method':
            num_locals += 1
        write_function(file, subroutine_name, num_locals)

        if subroutine_type == 'constructor':
            write_push(file, 'constant', num_locals)
            write_call(file, 'Memory.alloc', 1)

        if subroutine_type == 'method':
            # Since the first argument of a method is the object itself,
            # assign pointer[0] (this) to the first argument
            write_push(file, 'argument', 0)
            write_pop(file, 'pointer', 0)

        _compile_statements(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '}')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        # _write(file, '</subroutineBody>')

        # _write(file, '</subroutineDec>')
        token_type, token_val = _peek_stack_head(token_gen)

    return


def _compile_parameter_list(file, token_gen):
    # _write(file, '<parameterList>')

    token_type, token_val = _peek_stack_head(token_gen)
    if token_type in [IDENTIFIER, KEYWORD]:
        _type = token_val
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        name = token_val
        define(name, _type, 'argument')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        while (token_type, token_val) == (SYMBOL, ','):
            _pop(token_stack)  # _write_token(file, _pop(token_stack))

            token_type, token_val = _peek_stack_head(token_gen)
            assert token_type in [IDENTIFIER, KEYWORD]
            _type = token_val
            _pop(token_stack)  # _write_token(file, _pop(token_stack))

            token_type, token_val = _peek_stack_head(token_gen)
            assert token_type == IDENTIFIER
            name = token_val
            define(name, _type, 'argument')
            _pop(token_stack)  # _write_token(file, _pop(token_stack))
            token_type, token_val = _peek_stack_head(token_gen)

    # _write(file, '</parameterList>')
    return


def _compile_var_dec(file, token_gen):
    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) != (KEYWORD, 'var'):
        return 0

    # _write(file, '<varDec>')

    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type in [IDENTIFIER, KEYWORD]
    _type = token_val
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    name = token_val
    _pop(token_stack)  # _write_token(file, _pop(token_stack))
    define(name, _type, 'local')

    num_vars = 1
    token_type, token_val = _peek_stack_head(token_gen)
    while (token_type, token_val) == (SYMBOL, ','):
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert token_type == IDENTIFIER
        name = token_val
        define(name, _type, 'local')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        num_vars += 1
        token_type, token_val = _peek_stack_head(token_gen)

    assert (token_type, token_val) == (SYMBOL, ';')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</varDec>')
    _compile_var_dec(file, token_gen)
    return num_vars


def _compile_statements(file, token_gen):
    # _write(file, '<statements>')

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

    # _write(file, '</statements>')
    return


def _compile_let(file, token_gen):
    # _write(file, '<letStatement>')

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'let')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    symbol = token_val
    kind = kind_of(symbol)
    index = index_of(symbol)
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) == (SYMBOL, '['):

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '[')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        _compile_expression(file, token_gen)
        write_push(file, kind, index)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, ']')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        write_arithmetic(file, 'add')  # Add index + base of array

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '=')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        _compile_expression(file, token_gen)
        write_pop(file, 'temp', 0)  # store expression in temp 0
        write_pop(file, 'pointer', 1)  # NOQA store the register location of the array in 'that'
        write_push(file, 'temp', 0)
        write_pop(file, 'that', 0)

    else:
        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '=')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        _compile_expression(file, token_gen)
        write_pop(file, kind, index)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ';')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</letStatement>')
    return


def _compile_subroutine_call(file, token_gen):
    token_type, token_val = _peek_stack_head(token_gen)
    assert token_type == IDENTIFIER
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    subroutine_name = token_val
    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) == (SYMBOL, '.'):
        subroutine_name += '.'
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        subroutine_name += token_val
        assert token_type == IDENTIFIER
        _pop(token_stack)  # _write_token(file, _pop(token_stack))
        add_arg = False

    else:
        add_arg = True

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '(')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    num_args = _compile_expression_list(file, token_gen)
    if add_arg:
        num_args += 1

    write_call(file, subroutine_name, num_args)
    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ')')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))


def _compile_do(file, token_gen):

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'do')
    # _write(file, '<doStatement>')

    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    _compile_subroutine_call(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    write_pop(file, 'temp', 0)  # Ignore result from executing code
    assert (token_type, token_val) == (SYMBOL, ';')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</doStatement>')
    return


def _compile_if(file, token_gen):
    global while_num

    label_if_true = 'IF_TRUE_{}'.format(while_num)
    label_if_false = 'IF_FALSE_{}'.format(while_num)
    label_if_contiuation = 'IF_CONTINUATION_{}'.format(while_num)

    while_num += 1

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'if')
    # _write(file, '<ifStatement>')

    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '(')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    _compile_expression(file, token_gen)

    write_if(file, label_if_true)
    write_goto(file, label_if_false)
    write_label(file, label_if_true)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ')')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '{')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    _compile_statements(file, token_gen)

    write_goto(file, label_if_contiuation)
    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '}')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) == (KEYWORD, 'else'):

        write_label(file, label_if_false)
        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (KEYWORD, 'else')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '{')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        _compile_statements(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, '}')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</ifStatement>')
    write_label(file, label_if_contiuation)
    return


def _compile_while(file, token_gen):
    global while_num

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'while')
    # _write(file, '<whileStatement>')

    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    while_expression_label = 'WHILE_{}'.format(while_num)
    while_continuation_label = 'WHILE_END_{}'.format(while_num)

    while_num += 1

    write_label(file, while_expression_label)
    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '(')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    _compile_expression(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, ')')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    write_arithmetic(file, 'not')
    write_if(file, while_continuation_label)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '{')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    _compile_statements(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (SYMBOL, '}')
    write_goto(file, while_expression_label)
    write_label(file, while_continuation_label)
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    # _write(file, '</whileStatement>')
    return


def _compile_return(file, token_gen):

    token_type, token_val = _peek_stack_head(token_gen)
    assert (token_type, token_val) == (KEYWORD, 'return')
    # _write(file, '<returnStatement>')

    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) != (SYMBOL, ';'):
        _compile_expression(file, token_gen)

    else:
        write_pop(file, 'constant', 0)  # Push 0 if void

    token_type, token_val = _peek_stack_head(token_gen)

    assert (token_type, token_val) == (SYMBOL, ';')
    _pop(token_stack)  # _write_token(file, _pop(token_stack))

    write_return(file)
    # _write(file, '</returnStatement>')
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

    # _write(file, '<term>')

    if token_val in ['-', '~']:
        assert token_type == SYMBOL
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

        _compile_term(file, token_gen)
        command = {'-': 'neg', '~': 'not'}[token_val]
        write_arithmetic(file, command)

    elif token_type == INTEGER:
        _pop(token_stack)  # _write_token(file, _pop(token_stack))
        write_push(file, 'constant', token_val)

    elif token_type == STRING:
        _pop(token_stack)  # _write_token(file, _pop(token_stack))
        write_push(file, 'constant', len(token_val))
        write_call(file, 'String.new', 1)
        for letter in token_val:
            write_push(file, 'constant', ord(letter))
            write_call(file, 'String.appendChar', 2)

    elif token_val in term_keywords:
        if token_val in ['false', 'null']:
            write_push(file, 'constant', 0)
        elif token_val == 'true':
            write_push(file, 'constant', 1)
            write_arithmetic(file, 'neg')
        else:  # this command
            write_push(file, 'pointer', 0)
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

    elif (token_type, token_val) == (SYMBOL, '('):
        _pop(token_stack)  # _write_token(file, _pop(token_stack))
        _compile_expression(file, token_gen)

        token_type, token_val = _peek_stack_head(token_gen)
        assert (token_type, token_val) == (SYMBOL, ')')
        _pop(token_stack)  # _write_token(file, _pop(token_stack))

    else:
        future_token = token_gen.next()
        token_type, token_val = future_token
        if (token_type, token_val) == (SYMBOL, '['):

            token_type, token_val = _peek_stack_head(token_gen)
            kind = kind_of(token_val)
            index = index_of(token_val)
            assert token_type == IDENTIFIER
            _pop(token_stack)  # _write_token(file, _pop(token_stack))
            # _write_token(file, future_token)
            _compile_expression(file, token_gen)
            write_push(file, kind, index)
            write_arithmetic(file, 'add')
            write_pop(file, 'pointer', 1)
            write_push(file, 'that', 0)

            token_type, token_val = _peek_stack_head(token_gen)
            assert (token_type, token_val) == (SYMBOL, ']')
            _pop(token_stack)  # _write_token(file, _pop(token_stack))

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
            kind = kind_of(token_val)
            index = index_of(token_val)
            write_push(file, kind, index)
            _pop(token_stack)  # _write_token(file, _pop(token_stack))
            _push(token_stack, future_token)

    # _write(file, '</term>')


def _compile_expression(file, token_gen):
    operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    # _write(file, '<expression>')

    _compile_term(file, token_gen)

    token_type, token_val = _peek_stack_head(token_gen)
    if token_val in operators:

        _pop(token_stack)
        _compile_term(file, token_gen)
        if token_val == '*':
            write_call(file, 'Math.multiply', 2)
        elif token_val == '/':
            write_call(file, 'Math.divide', 2)
        else:
            command = {
                '+': 'add',
                '-': 'sub',
                '&': 'and',
                '|': 'or',
                '<': 'lt',
                '>': 'gt',
                '=': 'eq'
            }[token_val]
            write_arithmetic(file, command)

    # _write(file, '</expression>')
    return


def _compile_expression_list(file, token_gen):
    # _write(file, '<expressionList>')

    num_args = 0
    token_type, token_val = _peek_stack_head(token_gen)
    if (token_type, token_val) != (SYMBOL, ')'):
        _compile_expression(file, token_gen)
        num_args += 1
        token_type, token_val = _peek_stack_head(token_gen)
        while (token_type, token_val) == (SYMBOL, ','):
            _pop(token_stack)  # _write_token(file, _pop(token_stack))
            _compile_expression(file, token_gen)
            token_type, token_val = _peek_stack_head(token_gen)
            num_args += 1

    # _write(file, '</expressionList>')

    return num_args


def compile_file(file, token_gen):
    _compile_class(file, token_gen)
