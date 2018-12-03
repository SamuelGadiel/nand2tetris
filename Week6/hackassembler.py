## Criado por Samuel Gadiel de Ávila

INSTRUCTION_WIDTH = 16
OUTPUT_EXT = '.hack'
DESTINATION_INSTRUCTION_WIDTH = 3
JUMP_INSTRUCTION_WIDTH = 3
EOF = -1
NO_COMMAND = -2
A_COMMAND = 0
C_COMMAND = 1
L_COMMAND = 2

FIRST_VARIABLE_ADDRESS = 16


class SymbolTable:
    def __init__(self, file_path):
        self.file_path = file_path

        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576
        }

        for i in range(FIRST_VARIABLE_ADDRESS):
            self.table[f"R{i}"] = i

    def add_symbol(self, symbol, value):
        self.table[symbol] = value

    def first_pass(self):
        parser = Parser(self.file_path)
        parser.start_parsing()

        while True:
            command = parser.next_command()

            if command.type == EOF:
                break

            elif command.type == L_COMMAND:
                self.add_symbol(command.symbol, command.line)


class Command:
    def __init__(self):
        self.type = None
        self.line = 0

        self.symbol = None
        self.destination = None
        self.computation = None
        self.jump = None


class Parser:
    def __init__(self, input_file_name):
        self.input_file_name = input_file_name
        self._file_handle = None
        self.current_line = -1

    def start_parsing(self):
        self._file_handle = open(self.input_file_name, 'r')

    def next_command(self):
        command_str = self._file_handle.readline()

        command = Command()
        if not command_str:
            self._file_handle.close()
            command.type = EOF
            return command

        command_str = command_str.strip()
        if not command_str or command_str.startswith("//"):
            command.type = NO_COMMAND
            return command

        if "//" in command_str:
            command_str = command_str.split("//")[0]

        self.current_line += 1

        leading_character = command_str[0]

        if leading_character is "@":
            command.type = A_COMMAND
            command.symbol = command_str[1:]

        elif leading_character is "(":
            command.type = L_COMMAND
            command.symbol = command_str[1:-1]
            command.line = self.current_line
            self.current_line -= 1

        else:
            command.type = C_COMMAND
            if "=" not in command_str:
                if ";" not in command_str:
                    command.computation = command_str
                else:
                    command.computation, command.jump = list(map(str.strip, command_str.split(";")))
            else:
                if ";" not in command_str:
                    command.destination, command.computation = list(map(str.strip, command_str.split("=")))
                else:
                    dest, comp_jump = command_str.split("=")
                    comp, jump = comp_jump.split(";")
                    command.destination = dest.strip()
                    command.computation = comp.strip()
                    command.jump = jump.strip()

        return command


class Decoder:
    def __init__(self):
        self.COMP_TABLE = {
            "0": "101010",
            "1": "111111",
            "-1": "111010",
            "D": "001100",
            "A": "110000",
            "!D": "001101",
            "!A": "110001",
            "-D": "001111",
            "-A": "110011",
            "D+1": "011111",
            "A+1": "110111",
            "D-1": "001110",
            "A-1": "110010",
            "D+A": "000010",
            "D-A": "010011",
            "A-D": "000111",
            "D&A": "000000",
            "D|A": "010101"
        }

        self.DEST_TABLE = {
            None: bin(0)[2:],
            "M": bin(1)[2:],
            "D": bin(2)[2:],
            "MD": bin(3)[2:],
            "A": bin(4)[2:],
            "AM": bin(5)[2:],
            "AD": bin(6)[2:],
            "AMD": bin(7)[2:],
        }

        self.JMP_TABLE = {
            None: bin(0)[2:],
            "JGT": bin(1)[2:],
            "JEQ": bin(2)[2:],
            "JGE": bin(3)[2:],
            "JLT": bin(4)[2:],
            "JNE": bin(5)[2:],
            "JLE": bin(6)[2:],
            "JMP": bin(7)[2:],
        }

    def computation(self, computation):
        if computation in self.COMP_TABLE:
            bits = self.COMP_TABLE[computation]
        else:
            bits = self.COMP_TABLE[computation.replace("M", "A")]
        return bits

    def destination(self, destination):
        bits = self.DEST_TABLE[destination]
        padding = "0"*(DESTINATION_INSTRUCTION_WIDTH - len(str(bits)))

        destination_string = f"{padding}{bits}"
        return destination_string

    def jump(self, jump):
        bits = self.JMP_TABLE[jump]
        padding = "0" * (JUMP_INSTRUCTION_WIDTH - len(str(bits)))

        jump_string = f"{padding}{bits}"
        return jump_string


class HackAssembler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.parser = Parser(file_path)
        self.symbol_table = SymbolTable(file_path)
        self.output_file = None
        self.next_variable = FIRST_VARIABLE_ADDRESS

    def _open_output(self):
        output_file_path = f"{self.file_path[:-4]}{OUTPUT_EXT}"

        self.output_file = open(output_file_path, 'w')

    def _write_to_output(self, command):
        self.output_file.write(f"{command}\n")

    def _first_pass(self):
        self.symbol_table.first_pass()

    def parse(self):
        self.symbol_table.first_pass()

        self._open_output()
        self.parser.start_parsing()
        decoder = Decoder()

        while True:
            command = self.parser.next_command()
            binary_command = ""

            if command.type == EOF:
                self._finish_parsing()
                break
            elif command.type == NO_COMMAND:
                continue

            if command.type == A_COMMAND:
                if not command.symbol.isnumeric():
                    if command.symbol not in self.symbol_table.table:
                        self.symbol_table.add_symbol(command.symbol, self.next_variable)
                        self.next_variable += 1

                    value = self.symbol_table.table[command.symbol]

                else:
                    value = command.symbol

                binary_symbol = str(bin(int(value))[2:])
                padding = "0"*(INSTRUCTION_WIDTH - len(binary_symbol))
                binary_command = f"{padding}{binary_symbol}"

            elif command.type == L_COMMAND:
                pass

            else:
                if "M" in command.computation:
                    a_bit = 1
                else:
                    a_bit = 0
                padding = "111"
                comp_bits = decoder.computation(command.computation)
                dest_bits = decoder.destination(command.destination)
                jump_bits = decoder.jump(command.jump)

                binary_command = f"{padding}{a_bit}{comp_bits}{dest_bits}{jump_bits}"

            if len(binary_command) == INSTRUCTION_WIDTH:
                self._write_to_output(binary_command)

    def _finish_parsing(self):
        self.output_file.close()


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    assembler = HackAssembler(path)
    assembler.parse()
