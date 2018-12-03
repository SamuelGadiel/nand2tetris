#  This is what is called JackCompiler module in the book
import sys
import os

from tokenizer import tokenizer
from compilation_engine import compile_file


def _is_file(arg):
    return '.' in arg


def _is_jack_file(file):
    return file.split('.')[1] == 'jack'


def _get_jack_files(arg):
    if _is_file(arg):
        files = [arg]
    else:
        content_in_directory = \
            ['{}/'.format(arg) + content for content in os.listdir(arg)]
        files = [file for file in content_in_directory if _is_file(file)]

    return (file for file in files if _is_jack_file(file))


def _get_output_filename(arg):
    return '{}.vm'.format(arg.split('.jack')[0])

##################--------- DRIVER CODE  -------######################  # NOQA

if __name__ != '__main__':
    print 'Please run as a self-conatined program'

jack_files = _get_jack_files(sys.argv[1])

for file in jack_files:
    token_gen = tokenizer(file)
    output_file = open(_get_output_filename(file), 'w')
    compile_file(output_file, token_gen)
