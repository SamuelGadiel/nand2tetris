import os
import sys
from typing import TextIO as FileStream

EOF = -1
NO_COMMAND = -2


class CommandTypes:
    command = int

    ARITHMETIC_COMMAND = 1
    PUSH_COMMAND = 2
    POP_COMMAND = 3
    LABEL_COMMAND = 4
    GOTO_COMMAND = 5
    IF_COMMAND = 6
    FUNCTION_COMMAND = 7
    RETURN_COMMAND = 8
    CALL_COMMAND = 9

    COMMAND_TYPE = {
        'add': ARITHMETIC_COMMAND,
        'sub': ARITHMETIC_COMMAND,
        'neg': ARITHMETIC_COMMAND,
        'eq': ARITHMETIC_COMMAND,
        'gt': ARITHMETIC_COMMAND,
        'lt': ARITHMETIC_COMMAND,
        'and': ARITHMETIC_COMMAND,
        'or': ARITHMETIC_COMMAND,
        'not': ARITHMETIC_COMMAND,
        'push': PUSH_COMMAND,
        'pop': POP_COMMAND,
        'label': LABEL_COMMAND,
        'goto': GOTO_COMMAND,
        'if-goto': IF_COMMAND,
        'function': FUNCTION_COMMAND,
        'call': CALL_COMMAND,
        'return': RETURN_COMMAND
    }


class MemorySegments:
    SEGMENTS = {
        'local': 'LCL',
        'argument': 'ARG',
        'pointer': 3,
        'this': 'THIS',
        'that': 'THAT',
        'temp': 5,
    }


c = CommandTypes
m = MemorySegments


class Parser:
    def __init__(self, input_file: FileStream):
        self._input_file = input_file

        self.command = None
        self.first_argument = None
        self.second_argument = None

    def advance(self):
        line = self._input_file.readline()
        if not line:
            return EOF

        line = line.split('//')[0] \
                   .strip()

        if not line:
            return NO_COMMAND

        line = line.split()
        self.command = line[0]
        if len(line) > 1:
            self.first_argument = line[1]
        if len(line) == 3:
            self.second_argument = line[2]

    def close(self):
        self._input_file.close()


class CodeWriter:
    def __init__(self, output_file: FileStream):
        self._output_file = output_file

        self.current_file_name = None

        self.instruction_jump_labels = 0

    def write_arithmetic(self, command: str):
        i = self.instruction_jump_labels
        asm_instructions = []
        if command == 'add':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M+D',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]

        elif command == 'sub':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]

        elif command == 'neg':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'M=-M',
                '@SP',
                'M=M+1'
            ]

        elif command == 'eq':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',
                f"@EQ_{i}",
                'D;JEQ',
                '@SP',
                'A=M',
                'M=0',
                f"@CONTINUE_{i}",
                '0;JMP',
                f"(EQ_{i})",
                '@SP',
                'A=M',
                'M=-1',
                f"(CONTINUE_{i})",
                '@SP',
                'M=M+1'
            ]

        elif command == 'gt':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',
                f"@GT_{i}",
                'D;JGT',
                '@SP',
                'A=M',
                'M=0',
                f"@CONTINUE_{i}",
                '0;JMP',
                f"(GT_{i})",
                '@SP',
                'A=M',
                'M=-1',
                f"(CONTINUE_{i})",
                '@SP',
                'M=M+1'
            ]

        elif command == 'lt':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',
                f"@LT_{i}",
                'D;JLT',
                '@SP',
                'A=M',
                'M=0',
                f"@CONTINUE_{i}",
                '0;JMP',
                f"(LT_{i})",
                '@SP',
                'A=M',
                'M=-1',
                f"(CONTINUE_{i})",
                '@SP',
                'M=M+1'
            ]

        elif command == 'and':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=D&M',
                '@SP',
                'M=M+1'
            ]

        elif command == 'or':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=D|M',
                '@SP',
                'M=M+1'
            ]

        elif command == 'not':
            asm_instructions = [
                '@SP',
                'M=M-1',
                'A=M',
                'M=!M',
                '@SP',
                'M=M+1'
            ]

        self.instruction_jump_labels += 2

        asm_instructions = '\n'.join(asm_instructions)

        self._output_file.write(f"// {command}\n")
        self._output_file.write(f"{asm_instructions}\n")

    def write_push_pop(self, command_type: c.command, segment, index):
        asm_instructions = []
        command = ""

        if command_type is c.PUSH_COMMAND:
            command = 'push'
        elif command_type is c.POP_COMMAND:
            command = 'pop'

        if segment == 'constant' and command == 'push':
            asm_instructions = [
                f"@{index}",
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]

        elif segment == 'static':
            if command == 'push':
                asm_instructions = [
                    f"@{self.current_file_name}.{index}",
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            elif command == 'pop':
                asm_instructions = [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    f"@{self.current_file_name}.{index}",
                    'M=D'
                ]

        elif segment == 'pointer' or segment == 'temp':
            base_address = m.SEGMENTS[segment]
            if command == 'push':
                asm_instructions = [
                    f"@{base_address}",
                    'D=A',
                    f"@{index}",
                    'A=A+D',
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            elif command == 'pop':
                asm_instructions = [
                    f"@{base_address}",
                    'D=A',
                    f"@{index}",
                    'D=A+D',
                    '@R13',
                    'M=D',
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@R13',
                    'A=M',
                    'M=D'
                ]

        else:
            segment = m.SEGMENTS[segment]
            if command == 'push':
                asm_instructions = [
                    f"@{segment}",
                    'D=M',
                    f'@{index}',
                    f"A=A+D",
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            else:
                asm_instructions = [
                    f"@{segment}",
                    'D=M',
                    f"@{index}",
                    f"D=A+D",
                    '@R13',
                    'M=D',
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@R13',
                    'A=M',
                    'M=D'
                ]

        asm_instructions = '\n'.join(asm_instructions)

        self._output_file.write(f"// {command} {segment} {index}\n")
        self._output_file.write(f"{asm_instructions}\n")

    def close(self):
        self._output_file.close()


class VMTranslator:
    def __init__(self, output_file_name):
        self.writer = CodeWriter(open(output_file_name, 'w'))

    def parse_file(self, file_name):
        self.writer.current_file_name = file_name.strip('.vm')

        p = Parser(open(file_name, 'r'))

        while True:
            next_command = p.advance()
            if next_command is EOF:
                break

            elif next_command is not NO_COMMAND:
                command_type = c.COMMAND_TYPE[p.command]
                if command_type is c.ARITHMETIC_COMMAND:
                    self.writer.write_arithmetic(p.command)

                elif command_type is c.PUSH_COMMAND or command_type is c.POP_COMMAND:
                    self.writer.write_push_pop(command_type,
                                               p.first_argument, int(p.second_argument))

                else:
                    ...

    def end_translation(self):
        self.writer.close()


def main(path):
    output_path = f"{path.strip('.vm')}.asm"

    translator = VMTranslator(output_path)

    if os.path.isfile(path):
        translator.parse_file(path)

    else:
        files = [f for f in os.listdir(path) if os.path.isfile(f)]

        for file_name in files:
            translator.parse_file(file_name)

    translator.end_translation()


if __name__ == '__main__':
    path_ = sys.argv[1]
    main(path_)
