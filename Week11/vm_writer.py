
def write_push(file, segment, index):
    file.write('push {} {}\n'.format(segment, index))


def write_pop(file, segment, index):
    file.write('pop {} {}\n'.format(segment, index))


def write_arithmetic(file, command):
    file.write('{}\n'.format(command))


def write_label(file, label):
    file.write('label {}\n'.format(label))


def write_goto(file, label):
    file.write('goto {}\n'.format(label))


def write_if(file, label):
    file.write('if-goto {}\n'.format(label))


def write_call(file, name, num_args):
    file.write('call {} {}\n'.format(name, num_args))


def write_function(file, name, num_locals):
    file.write('function {} {}\n'.format(name, num_locals))


def write_return(file):
    file.write('return\n')
