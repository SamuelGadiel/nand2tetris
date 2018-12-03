import os
import sys
from typing import TextIO as FileStream

EOF = -2
NO_COMMAND = -1
DEBUG = False

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
        'stack_pointer_init': 256
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

        self.instruction_index = 0

        self.current_function_name = None

        self.idx = 0

    def _write_instructions(self, comment, instructions):
        instructions = [instruction if instruction.startswith('(')
                        else f"\t{instruction}"
                        for instruction in instructions]

        if DEBUG:
            i = []
            for instruction in instructions:
                if not instruction.startswith('('):
                    i.append(f"{self.idx}{instruction}")
                    self.idx += 1
                else:
                    i.append(instruction)
            instructions = i

        instructions = '\n'.join(instructions)
        self._output_file.write(f"// {comment}\n")
        self._output_file.write(f"{instructions}\n")

    def write_init(self):
        sp_init = m.SEGMENTS['stack_pointer_init']
        asm_instructions = [
            f"@{sp_init}",
            'D=A',
            '@SP',
            'M=D',
            '@Sys.init',
            '0;JMP'
        ]

        comment = 'Bootstrap'
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_arithmetic(self, command: str):
        i = self.instruction_index
        self.instruction_index += 1
        asm_instructions = []
        if command == 'add':
            asm_instructions = [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'D=M+D',
                '@SP',
                'M=M+1',
                'A=M-1',
                'M=D',
            ]

        elif command == 'sub':
            asm_instructions = [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'D=M-D',
                '@SP',
                'M=M+1',
                'A=M-1',
                'M=D',
            ]

        elif command == 'neg':
            asm_instructions = [
                '@SP',
                'A=M-1',
                'M=-M'
            ]

        elif command == 'eq':
            asm_instructions = [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
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
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
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
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
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
                'AM=M-1',
                'D=M',
                '@SP',
                'A=M-1',
                'M=D&M'
            ]

        elif command == 'or':
            asm_instructions = [
                '@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'A=M-1',
                'M=D|M'
            ]

        elif command == 'not':
            asm_instructions = [
                '@SP',
                'A=M-1',
                'M=!M'
            ]

        self._write_instructions(comment=command, instructions=asm_instructions)

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
                'M=M+1',
                'A=M-1',
                'M=D'
            ]

        elif segment == 'static':
            if command == 'push':
                asm_instructions = [
                    f"@{self.current_file_name}.{index}",
                    'D=M',
                    '@SP',
                    'M=M+1',
                    'A=M-1',
                    'M=D'
                ]
            elif command == 'pop':
                asm_instructions = [
                    '@SP',
                    'AM=M-1',
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
                    'M=M+1',
                    'A=M-1',
                    'M=D'
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
                    'AM=M-1',
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
                    'M=M+1',
                    'A=M-1',
                    'M=D'
                ]
            elif command == 'pop':
                asm_instructions = [
                    f"@{segment}",
                    'D=M',
                    f"@{index}",
                    f"D=A+D",
                    '@R13',
                    'M=D',
                    '@SP',
                    'AM=M-1',
                    'D=M',
                    '@R13',
                    'A=M',
                    'M=D'
                ]

        comment = f"{command} {segment} {index}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_label(self, label):
        asm_instructions = [
            f"({self.current_function_name}${label})"
        ]

        comment = f"label {self.current_function_name}${label}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_goto(self, label):
        asm_instructions = [
            f"@{self.current_function_name}${label}",
            '0;JMP'
        ]

        comment = f"goto {self.current_function_name}${label}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_if(self, label):
        asm_instructions = [
            '@SP',
            'AM=M-1',
            'D=M',
            f"@{self.current_function_name}${label}",
            'D;JNE'
        ]

        comment = f"if-goto {self.current_function_name}${label}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_call(self, function_name, n_arguments):
        i = self.instruction_index
        self.instruction_index += 1
        asm_instructions = [
            f"@{function_name}.return_{i}",
            'D=A',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',
            '@LCL',
            'D=M',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',
            '@ARG',
            'D=M',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',
            '@THIS',
            'D=M',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',
            '@THAT',
            'D=M',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=D',
            'D=A+1',
            f"@{5+n_arguments}",
            'D=D-A',
            '@ARG',
            'M=D',
            '@SP',
            'D=M',
            '@LCL',
            'M=D',
            f"@{function_name}",
            '0;JMP',
            f"({function_name}.return_{i})"
        ]

        comment = f"call {function_name} {n_arguments}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_function(self, function_name, n_locals):
        asm_instructions = [
            f"({function_name})",
            f"@{function_name}.locals",
            'M=0',
            f"({function_name}.locals_loop)",
            f"@{n_locals}",
            'D=A',
            f"@{function_name}.locals",
            'D=D-M',
            f"@{function_name}.end_locals_loop",
            'D;JEQ',
            '@SP',
            'M=M+1',
            'A=M-1',
            'M=0',
            f"@{function_name}.locals",
            'M=M+1',
            f"@{function_name}.locals_loop",
            '0;JMP',
            f"({function_name}.end_locals_loop)"
        ]
        self.current_function_name = function_name

        comment = f"function {function_name} {n_locals}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def write_return(self):
        frame = 'R14'
        ret = 'R15'
        asm_instructions = [
            '@LCL',
            'D=M',
            f"@{frame}",
            'M=D',
            '@5',
            'A=D-A',
            'D=M',
            f"@{ret}",
            'M=D',
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@ARG',
            'A=M',
            'M=D',
            'D=A+1',
            '@SP',
            'M=D',
            f"@{frame}",
            'AM=M-1',
            'D=M',
            '@THAT',
            'M=D',
            f"@{frame}",
            'AM=M-1',
            'D=M',
            '@THIS',
            'M=D',
            f"@{frame}",
            'AM=M-1',
            'D=M',
            '@ARG',
            'M=D',
            f"@{frame}",
            'A=M-1',
            'D=M',
            '@LCL',
            'M=D',
            f"@{ret}",
            'A=M',
            '0;JMP'
        ]

        comment = f"return from {self.current_function_name}"
        self._write_instructions(comment=comment, instructions=asm_instructions)

    def close(self):
        self._output_file.close()


class VMTranslator:
    def __init__(self, output_file_name):
        self._writer = CodeWriter(open(output_file_name, 'w'))

    def write_init(self):
        self._writer.write_init()

    def parse_file(self, file_name):
        self._writer.current_file_name = os.path.split(file_name.strip('.vm'))[1]

        p = Parser(open(file_name, 'r'))

        while True:
            next_command = p.advance()
            if next_command is EOF:
                break

            elif next_command is not NO_COMMAND:
                command_type = c.COMMAND_TYPE[p.command]
                if command_type is c.ARITHMETIC_COMMAND:
                    self._writer.write_arithmetic(p.command)

                elif command_type is c.PUSH_COMMAND or command_type is c.POP_COMMAND:
                    self._writer.write_push_pop(command_type,
                                                p.first_argument, int(p.second_argument))

                elif command_type is c.LABEL_COMMAND:
                    self._writer.write_label(p.first_argument)

                elif command_type is c.GOTO_COMMAND:
                    self._writer.write_goto(p.first_argument)

                elif command_type is c.IF_COMMAND:
                    self._writer.write_if(p.first_argument)

                elif command_type is c.FUNCTION_COMMAND:
                    self._writer.write_function(p.first_argument, int(p.second_argument))

                elif command_type is c.CALL_COMMAND:
                    self._writer.write_call(p.first_argument, int(p.second_argument))

                elif command_type is c.RETURN_COMMAND:
                    self._writer.write_return()

    def end_translation(self):
        self._writer.close()


def main(path):
    head, tail = os.path.split(path)

    if head:
        os.chdir(head)

    output_path = f"{tail.strip('.vm')}.asm"

    translator = VMTranslator(output_path)

    if os.path.isfile(path):
        translator.parse_file(path)

    else:

        vm_files = [f for f in os.listdir(path) if f.endswith('.vm')]
        translator.write_init()

        for file_name in vm_files:
            translator.parse_file(os.path.join(head, tail, file_name))

    translator.end_translation()


if __name__ == '__main__':
    path_ = sys.argv[1]
    main(path_)
