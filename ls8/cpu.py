"""CPU functionality."""

import sys

ADD = 0b10100000
CALL = 0b01010000
HLT = 0b00000001
LDI = 0b10000010
MUL = 0b10100010
POP = 0b01000110
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0  # program counter
        self.ram = [0] * 256
        self.halted = False

    def load(self, filename):
        """Load a program into memory."""
        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    bin_num = comment_split[0]
                    try:
                        x = int(bin_num.strip(), 2)
                        self.ram_write(address, x)
                        address += 1
                    except:
                        continue
        except FileNotFoundError:
            print('File not found.')

    def alu(self, instruction, reg_a, reg_b):
        """ALU operations."""

        if instruction == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif instruction == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def run(self):
        """
        Run the CPU - Execution Sequence
        1. The instruction pointed to by the PC is fetched from RAM, decoded, and executed.
        2. If the instruction does not set the PC itself, the PC is advanced to point to the subsequent instruction.
        3. If the CPU is not halted by a HLT instruction, go to step 1.
        """
        while not self.halted:
            instruction = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.execute_instruction(instruction, operand_a, operand_b)

    def execute_instruction(self, instruction, operand_a, operand_b):
        """
        Instructions code.
        """
        pc_increment = ((instruction >> 6) & 0b11) + 1

        if instruction == ADD:
            self.alu(instruction, operand_a, operand_b)
            self.pc += pc_increment
        elif instruction == CALL:
            self.reg[7] -= 1
            self.ram_write(self.reg[7], self.pc + 2)
            self.pc = self.reg[operand_a]
        elif instruction == HLT:
            self.halted = True
        elif instruction == LDI:
            self.reg[operand_a] = operand_b
            self.pc += pc_increment
        elif instruction == MUL:
            self.alu(instruction, operand_a, operand_b)
            self.pc += pc_increment
        elif instruction == POP:
            self.reg[operand_a] = self.ram_read(self.reg[7])
            self.reg[7] += 1
            self.pc += pc_increment
        elif instruction == PRN:
            print(self.reg[operand_a])
            self.pc += pc_increment
        elif instruction == PUSH:
            self.reg[7] -= 1
            self.ram_write(self.reg[7], self.reg[operand_a])
            self.pc += pc_increment
        elif instruction == RET:
            self.pc = self.ram_read(self.reg[7])
        else:
            print(f'Unkown instruction {instruction}')
