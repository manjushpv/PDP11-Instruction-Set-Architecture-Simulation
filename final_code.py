global StackPointer_max

Reg = ['Reg0', 'Reg1', 'Reg2', 'Reg3', 'Reg4', 'Reg5', 'Reg6', 'Reg7']
R = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
memory = ['00000000'] * 64 * 1024
tracefile = open("/Users/manjush/Desktop/trace.txt", "w")
# tracefile object
Readaddress = None
source_data = None
destination_data = None
Count = 0
# rcount = 0
# wcount = 0
Src_flag = 0

instruction = {'type': None, 'opcode': None, 'source_mode': None, 'source_reg': None, 'destination_mode': None,
               'destination_reg': None, 'offset': None}
double_operand_mnemonic = ['001', '010', '011', '100', '101', '110']
Mnemonic = {'001': 'MOV', '010': 'CMP', '011': 'BIT', '100': 'BIC', '101': 'BIS', '110': 'ADD', '0000000011': 'SWAB',
            '01000': 'CLR',
            '01001': 'COM', '01010': 'INC', '01011': 'DEC', '01100': 'NEG', '01101': 'ADC', '01110': 'SBC',
            '01111': 'TST', '10000': 'ROR', '10001': 'ROL', '10010': 'ASR', '10011': 'ASL', '10111': 'SXT',
            '00000001': 'BR', '00000010': 'BNE', '00000011': 'BEQ', '10000000': 'BPL', '10000001': 'BMI',
            '10000100': 'BVC', '10000101': 'BVS', '10000110': 'BHIS', '10000110': 'BCC', '10000111': 'BLO',
            '10000111': 'BCS', '00000100': 'BGE', '00000101': 'BLT', '00000110': 'BGT', '0000011': 'BLE',
            '10000010': 'BHI', '10000011': 'BLOS', '10100000': 'NOP',
            '10100001': 'CLC', '10100010': 'CLV', '10100100': 'CLZ', '10101000': 'CLN', '10101111': 'CCC',
            '10110000': 'NOP',
            '10110001': 'SEC', '10110010': 'SEV', '10110100': 'SEZ', '10111000': 'SEN', '10111111': 'SCC',
            '00000': 'JSR', '00001': 'JSR',
            '00010': 'JSR', '00011': 'JSR', '00100': 'JSR', '00101': 'JSR', '00110': 'JSR', '00111': 'JSR',
            '10001000': 'EMT', '0000000010000': 'RTS'}
flags = {'N': 0, 'Z': 0, 'V': 0, 'C': 0}

IR = None


def loadInstr(source):
    inputfile = open(source, "r")

    for instruction_word in inputfile:
        binary_instruction_word = format(int(instruction_word[1:7], 8), '016b')
        if (instruction_word[0] == '@'):
            Data_Pointer = int(binary_instruction_word, 2)
            i = Data_Pointer
        elif (instruction_word[0] == '*'):
            R[7] = int(binary_instruction_word, 2)
        elif (instruction_word[0] == '-'):
            memory[i] = binary_instruction_word[8:]
            i += 1
            memory[i] = binary_instruction_word[:8]
            i += 1
        else:
            print("Invalid Instruction")


def decode(instruction_reg):
    obj_IT = Instruction_Type()
    if instruction_reg[1:4] in double_operand_mnemonic:
        obj_IT.double_operand(instruction_reg)
        return 'double_operand'
    elif instruction_reg[:10] == '0000000011':
        obj_IT.swab(instruction_reg)
        return 'swab'

    elif instruction_reg[1:5] == '0001':
        obj_IT.single_operand(instruction_reg)
        return 'single_operand'
    elif instruction_reg[:13] == '0000000010000':
        obj_IT.RTS(instruction_reg)
        return 'RTS'
    elif instruction_reg[:10] == '0000000010':
        obj_IT.psw(instruction_reg)
        return 'psw'
    elif instruction_reg[1:5] == '0000':
        obj_IT.branch(instruction_reg)
        return 'branch'


def writeTrace(Operation, Memaddress):
    temp = str(Operation) + ' ' + format(Memaddress, '06o')
    tracefile.write(temp + '\n')
    return


class Instruction_Type:

    def double_operand(self, instruction_reg):
        instruction['type'] = instruction_reg[0:1]
        instruction['opcode'] = instruction_reg[1:4]
        instruction['source_mode'] = instruction_reg[4:7]
        instruction['source_reg'] = instruction_reg[7:10]
        instruction['destination_mode'] = instruction_reg[10:13]
        instruction['destination_reg'] = instruction_reg[13:]

    def single_operand(self, instruction_reg):
        if (instruction_reg[:8] == '10001000'):
            instruction['opcode'] = instruction_reg[:8]
        else:
            instruction['type'] = instruction_reg[0:1]
            instruction['opcode'] = instruction_reg[5:10]
            instruction['destination_mode'] = instruction_reg[10:13]
            instruction['destination_reg'] = instruction_reg[13:]

    def branch(self, instruction_reg):
        instruction['opcode'] = instruction_reg[:8]  # changed from [5:8]to [1:8] since mnemonic duplication problem
        instruction['offset'] = instruction_reg[8:]

    def RTS(self, instruction_reg):
        instruction['destination_reg'] = instruction_reg[13:]
        instruction['opcode'] = '0000000010000'

    def psw(self, instruction_reg):
        instruction['opcode'] = instruction_reg[8:]

    def swab(self, instruction_reg):
        instruction['opcode'] = instruction_reg[:10]
        instruction['destination_mode'] = instruction_reg[10:13]
        instruction['destination_reg'] = instruction_reg[13:]


class Addressing_Modes:
    Address = None
    Data = None
    Readaddress = None

    ##def __init__(self):

    def set_Addressing_Mode(self, AM_value, register_number, data):
        if AM_value == '000':
            self.register(register_number)
        elif AM_value == '001':
            if register_number == 6:
                self.deferred_SP()
            else:
                self.register_deferred(register_number)
        elif AM_value == '010':
            if register_number == 7:
                self.immediate_PC()
            elif register_number == 6:
                if R[6] == StackPointer_max:
                    print('Empty stack')
                else:
                    self.autoincrement_SP()
            else:
                self.autoincrement(register_number)
        elif AM_value == '011':
            if register_number == 6:
                self.autoincrement_deferred_SP()
            elif register_number == 7:
                self.absolute_PC()
            else:
                self.autoincrement_deferred(register_number)
        elif AM_value == '100':
            if register_number == 6:
                self.autodecrement_SP(data)
            else:
                self.autodecrement(register_number)
        elif AM_value == '101':
            self.autodecrement_deferred(register_number)
        elif AM_value == '110':
            if register_number == 6:
                self.indexed_SP()
            elif register_number == 7:
                self.relative_PC()
            else:
                self.index(register_number)
        elif AM_value == '111':
            if register_number == 6:
                self.indexed_deferred_SP()
            elif register_number == 7:
                self.relative_deferred_PC()
            else:
                self.index_deferred(register_number)
        else:
            print('invalid addressing mode')

    def register(self, register_number):
        self.Data = bin(R[register_number])[2:].zfill(16)

    def register_deferred(self, register_number):
        self.Address = R[register_number]
        self.Data = memory[self.Address + 1] + memory[self.Address]
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autoincrement(self, register_number):
        self.Address = R[register_number]
        self.Data = memory[self.Address + 1] + memory[self.Address]
        R[register_number] += 2  ##hardcoded addition for word operation
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autoincrement_deferred(self, register_number):
        mem_ref = R[register_number]

        writeTrace(0, mem_ref)
        # rcount+=1
        self.Address = int((memory[mem_ref + 1] + memory[mem_ref]), 2)
        self.Data = memory[self.Address + 1] + memory[self.Address]  ##handle memory[None] exception
        R[register_number] += 2  ##hardcoded addition for word operation
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autodecrement(self, register_number):
        R[register_number] -= 2  ##hardcoded subtraction for word operation
        self.Address = R[register_number]
        self.Data = memory[self.Address + 1] + memory[self.Address]
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autodecrement_deferred(self, register_number):
        R[register_number] -= 2  ##hardcoded subtraction for word operation
        mem_ref = R[register_number]
        writeTrace(0, mem_ref)
        # rcount+=1
        self.Address = int((memory[mem_ref + 1] + memory[mem_ref]), 2)
        self.Data = memory[self.Address + 1] + memory[self.Address]  ##handle memory[None] exception
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def index(self, register_number):
        mem_ref = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        R[7] = R[7] + 2
        self.Address = R[register_number] + mem_ref
        self.Data = memory[self.Address + 1] + memory[self.Address]
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def index_deferred(self, register_number):
        mem_ref = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        R[7] = R[7] + 2
        addr_ref = R[register_number] + mem_ref
        writeTrace(0, addr_ref)
        # rcount+=1
        self.Address = int((memory[addr_ref + 1] + memory[addr_ref]), 2)
        self.Data = memory[self.Address + 1] + memory[self.Address]  ##handle memory[None] exception
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def deferred_SP(self):
        self.Address = R[6]
        self.Data = memory[self.Address] + memory[self.Address - 1]
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autoincrement_SP(self):
        self.Address = R[6]
        self.Data = memory[self.Address] + memory[self.Address - 1]
        # memory[StackPointer] = memory[StackPointer - 1] = None
        R[6] = R[6] + 2
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autoincrement_deferred_SP(self):
        self.Address = int((memory[R[6]] + memory[R[6] - 1]), 2)
        writeTrace(0, R[6])
        # rcount+=1
        self.Data = memory[self.Address + 1] + memory[self.Address]  ##is this referring to memory
        # memory[StackPointer] = memory[StackPointer - 1] = None
        R[6] = R[6] + 2
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def autodecrement_SP(self, data):
        R[6] = R[6] - 2
        self.Address = R[6]  ##how to send the address pointer for stack for write operation
        memory[self.Address - 1] = data[8:]
        memory[self.Address] = data[:8]
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def indexed_SP(self):
        addr_ref = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        if (R[6] + addr_ref) >= 2 ** 16:
            self.Address = R[6] + addr_ref - 2 ** 16
        else:
            self.Address = R[6] + addr_ref
        self.Data = memory[self.Address] + memory[self.Address - 1]  ##is this referring to stack
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def indexed_deferred_SP(self):
        addr_ref = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        # mem_ref = int((memory[self.ProgramCounter + 1] + memory[self.ProgramCounter]), 2)
        mem_ref = R[6] + addr_ref
        writeTrace(0, mem_ref)
        # rcount+=1

        if (int((memory[mem_ref + 1] + memory[mem_ref]), 2)) >= 2 ** 16:
            self.Address = int((memory[mem_ref + 1] + memory[mem_ref]), 2) - 2 ** 16
        else:
            self.Address = int((memory[mem_ref + 1] + memory[mem_ref]), 2)  ##is this referring to memory
        self.Data = memory[self.Address + 1] + memory[self.Address]  ##is this referring to memory
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def immediate_PC(self):
        self.Address = R[7];
        R[7] = R[7] + 2
        self.Data = (memory[self.Address + 1] + memory[self.Address])
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount=#rcount+1

    def absolute_PC(self):
        self.Address = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        R[7] = R[7] + 2
        self.Data = (memory[self.Address + 1] + memory[self.Address])
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def relative_PC(self):
        mem_ref = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        R[7] = R[7] + 2
        if (mem_ref + R[7]) >= 2 ** 16:
            self.Address = mem_ref + R[7] - 2 ** 16
        else:
            self.Address = mem_ref + R[7]
        self.Data = memory[self.Address + 1] + memory[self.Address]
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1

    def relative_deferred_PC(self):
        addr_ref = int((memory[R[7] + 1] + memory[R[7]]), 2)
        writeTrace(0, R[7])
        # rcount+=1
        R[7] = R[7] + 2
        mem_ref = addr_ref + R[7]
        writeTrace(0, mem_ref)
        # rcount+=1
        if (int((memory[mem_ref + 1] + memory[mem_ref]), 2) >= 2 ** 16):
            self.Address = int((memory[mem_ref + 1] + memory[mem_ref]), 2) - 2 ** 16
        else:
            self.Address = int((memory[mem_ref + 1] + memory[mem_ref]), 2)
        self.Data = memory[self.Address]
        # writeTrace(0, self.Address)
        self.Readaddress = self.Address
        if Src_flag:
            writeTrace(0, self.Address)
            # rcount+=1


class Operation:

    def set_Operation(self, opcode, source_data, destination_data):

        if Mnemonic[opcode] == 'MOV':
            return self.Mov(source_data)
        elif Mnemonic[opcode] == 'CMP':
            self.Cmp(source_data, destination_data)
        elif Mnemonic[opcode] == 'BIT':
            self.Bit(source_data, destination_data)
        elif Mnemonic[opcode] == 'BIC':
            return self.Bic(source_data, destination_data)
        elif Mnemonic[opcode] == 'BIS':
            return self.Bis(source_data, destination_data)
        elif Mnemonic[opcode] == 'ADD':
            return self.Add(source_data, destination_data)
        elif Mnemonic[opcode] == 'SWAB':
            return self.Swab(destination_data)
        elif Mnemonic[opcode] == 'JSR':
            return self.Jsr(destination_data)
        elif Mnemonic[opcode] == 'EMT':
            return self.emt(destination_data)
        elif Mnemonic[opcode] == 'CLR':
            return self.Clr()
        elif Mnemonic[opcode] == 'COM':
            return self.Com(destination_data)
        elif Mnemonic[opcode] == 'INC':
            return self.Inc(destination_data)
        elif Mnemonic[opcode] == 'DEC':
            return self.Dec(destination_data)
        elif Mnemonic[opcode] == 'NEG':
            return self.Neg(destination_data)
        elif Mnemonic[opcode] == 'ADC':
            return self.Adc(destination_data)
        elif Mnemonic[opcode] == 'SBC':
            return self.Sbc(destination_data)
        elif Mnemonic[opcode] == 'TST':
            return self.tst(destination_data)
        elif Mnemonic[opcode] == 'ROR':
            return self.Ror(destination_data)
        elif Mnemonic[opcode] == 'ROL':
            return self.Rol(destination_data)
        elif Mnemonic[opcode] == 'ASR':
            return self.Asr(destination_data)
        elif Mnemonic[opcode] == 'ASL':
            return self.Asl(destination_data)
        elif Mnemonic[opcode] == 'SXT':
            return self.Axt(destination_data)
        elif Mnemonic[opcode] == 'BR':
            return self.Br(destination_data)
        elif Mnemonic[opcode] == 'BEQ':
            return self.Beq(destination_data)
        elif Mnemonic[opcode] == 'BNE':
            return self.Bne(destination_data)
        elif Mnemonic[opcode] == 'BPL':
            return self.Bpl(destination_data)
        elif Mnemonic[opcode] == 'BMI':
            return self.Bmi(destination_data)
        elif Mnemonic[opcode] == 'BVC':
            return self.Bvc(destination_data)
        elif Mnemonic[opcode] == 'BVS':
            return self.Bvs(destination_data)
        elif Mnemonic[opcode] == 'BHIS':
            return self.Bhis(destination_data)
        elif Mnemonic[opcode] == 'BCC':
            return self.Bcc(destination_data)
        elif Mnemonic[opcode] == 'BLO':
            return self.Blo(destination_data)
        elif Mnemonic[opcode] == 'BCS':
            return self.Bcs(destination_data)
        elif Mnemonic[opcode] == 'BGE':
            return self.Bge(destination_data)
        elif Mnemonic[opcode] == 'BLT':
            return self.Blt(destination_data)
        elif Mnemonic[opcode] == 'BGT':
            return self.Bgt(destination_data)
        elif Mnemonic[opcode] == 'BLE':
            return self.Ble(destination_data)
        elif Mnemonic[opcode] == 'BHI':
            return self.Bhi(destination_data)
        elif Mnemonic[opcode] == 'BLOS':
            return self.Blos(destination_data)  ##psw below
        elif Mnemonic[opcode] == 'NOP':
            return self.Nop(destination_data)
        elif Mnemonic[opcode] == 'CLC':
            return self.Clc()
        elif Mnemonic[opcode] == 'CLV':
            return self.Clv()
        elif Mnemonic[opcode] == 'CLZ':
            return self.Clz()
        elif Mnemonic[opcode] == 'CLN':
            return self.Cln()
        elif Mnemonic[opcode] == 'CCC':
            return self.Ccc()
        elif Mnemonic[opcode] == 'SEC':
            return self.Sec()
        elif Mnemonic[opcode] == 'SEV':
            return self.Sev()
        elif Mnemonic[opcode] == 'SEZ':
            return self.Sez()
        elif Mnemonic[opcode] == 'SEN':
            return self.Sen()
        elif Mnemonic[opcode] == 'SCC':
            return self.Scc()

    ##psw instructions:

    def Nop(self):
        return

    def Clc(self):
        flags['C'] = 0
        return

    def Clv(self):
        flags['V'] = 0
        return

    def Cln(self):
        flags['N'] = 0
        return

    def Clz(self):
        flags['Z'] = 0
        return

    def Sec(self):
        flags['C'] = 1
        return

    def Sev(self):
        flags['V'] = 1
        return

    def Sen(self):
        flags['N'] = 1
        return

    def Sez(self):
        flags['Z'] = 1
        return

    def Scc(self):
        flags['N'] = 1
        flags['C'] = 1
        flags['V'] = 1
        flags['Z'] = 1
        return

    def Ccc(self):
        flags['N'] = 0
        flags['C'] = 0
        flags['V'] = 0
        flags['Z'] = 0
        return

    def Mov(self, source_data):
        flags['V'] = 0
        if source_data == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0

        if source_data >= 2 ** 15:
            flags['N'] = 1
        else:
            flags['N'] = 0

        return source_data

    def MovB(self, source_data):
        flags['V'] = 0
        if source_data == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0

        if source_data >= 2 ** 15:
            flags['N'] = 1
        else:
            flags['N'] = 0

        return source_data

    def Cmp(self, source_data, destination_data):
        # source_bin = bin(source_data)[2:].zfill(16)
        # dest_bin = bin(destination_data)[2:].zfill(16)
        temp = source_data - destination_data
        # temp_bin = bin(temp)[2:].zfill(17)
        if temp < 0:
            flags['N'] = 1
            flags['C'] = 1
        else:
            flags['N'] = 0
            flags['C'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp >= (2 ** 15) or (temp < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0

    def CmpB(self, source_data, destination_data):
        # source_bin = bin(source_data)[2:].zfill(16)
        # dest_bin = bin(destination_data)[2:].zfill(16)
        temp = source_data - destination_data
        # temp_bin = bin(temp)[2:].zfill(17)
        if temp < 0:
            flags['N'] = 1
            flags['C'] = 1
        else:
            flags['N'] = 0
            flags['C'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp >= (2 ** 15) or (temp < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0

    def Bit(self, source_data, destination_data):
        if (source_data < 0):
            source_data = source_data + 2 ** 16
        if (destination_data < 0):
            destination_data = destination_data + 2 ** 16
        temp = source_data & destination_data
        flags['V'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if temp in range(2 ** 15, 2 ** 16):
            flags['N'] = 1
        else:
            flags['N'] = 0

    def BitB(self, source_data, destination_data):
        if (source_data < 0):
            source_data = source_data + 2 ** 16
        if (destination_data < 0):
            destination_data = destination_data + 2 ** 16
        temp = source_data & destination_data
        flags['V'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if temp in range(2 ** 15, 2 ** 16):
            flags['N'] = 1
        else:
            flags['N'] = 0

    def Bic(self, source_data, destination_data):
        if (source_data < 0):
            source_data = source_data + 2 ** 16
        if (destination_data < 0):
            destination_data = destination_data + 2 ** 16
        temp = ~source_data & destination_data
        flags['V'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if temp in range(2 ** 15, 2 ** 16):
            flags['N'] = 1
        else:
            flags['N'] = 0
        return temp

    def BicB(self, source_data, destination_data):
        if (source_data < 0):
            source_data = source_data + 2 ** 16
        if (destination_data < 0):
            destination_data = destination_data + 2 ** 16
        temp = ~source_data & destination_data
        flags['V'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if temp in range(2 ** 15, 2 ** 16):
            flags['N'] = 1
        else:
            flags['N'] = 0
        return temp

    def Bis(self, source_data, destination_data):
        if (source_data < 0):
            source_data = source_data + 2 ** 16
        if (destination_data < 0):
            destination_data = destination_data + 2 ** 16
        temp = source_data | destination_data
        flags['V'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if temp in range(2 ** 15, 2 ** 16):
            flags['N'] = 1
        else:
            flags['N'] = 0
        return temp

    def BisB(self, source_data, destination_data):
        if (source_data < 0):
            source_data = source_data + 2 ** 16
        if (destination_data < 0):
            destination_data = destination_data + 2 ** 16
        temp = source_data | destination_data
        flags['V'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if temp in range(2 ** 15, 2 ** 16):
            flags['N'] = 1
        else:
            flags['N'] = 0
        return temp

    def Add(self, source_data, destination_data):
        if instruction['type'] == '0':
            temp = source_data + destination_data
        else:
            temp = destination_data - source_data
        if temp < 0:
            flags['N'] = 1
            flags['C'] = 1
        else:
            flags['N'] = 0
            flags['C'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp >= (2 ** 15) or (temp < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0

        return temp

    ############# single operand instructions ##################

    def Jsr(self, destination_data):
        tempreg = int((instruction['opcode'][2:5]), 2)
        temp = format(R[tempreg], '016b')
        memory[R[6]] = temp[:8]
        memory[R[6] - 1] = temp[8:]
        R[6] -= 2
        writeTrace(1, R[6])
        # wcount+=1
        R[tempreg] = R[7]
        # R[7] = int(destination_data, 2)
        return

    def Emt(self, destination_data):
        R[6] -= 2  ## stores PS at sp-2 location
        memory[R[6]] = R[7][:8]
        memory[R[6] - 1] = R[7][8:]  ##PC stored to stack pointer
        R[6] -= 2  ##SP increments
        R[7] = int(memory[30], 2)  ##PC gets value from trap vector at mem[30]
        ##keeping NZCV as it is since they are to be loaded from trap vector
        return

    def Clr(self):
        flags['N'] = 0
        flags['Z'] = 1
        flags['C'] = 0
        flags['V'] = 0
        return 0

    def ClrB(self):
        flags['N'] = 0
        flags['Z'] = 1
        flags['C'] = 0
        flags['V'] = 0
        return 0

    def Swab(self, destination_data):
        temp = destination_data[8:] + destination_data[:8]
        if temp[8] == '1':
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (temp[8:] == '00000000'):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = 0
        flags['C'] = 0
        return int(temp, 2)

    def Com(self, destination_data):
        result = int(destination_data, 2)
        result = (-result - 1)
        if result < (0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if result == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['C'] = 1
        flags['V'] = 0
        return result

    def ComB(self, destination_data):
        result = int(destination_data, 2)
        result = (-result - 1)
        if result < (0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if result == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['C'] = 1
        flags['V'] = 0
        return result

    def Inc(self, destination_data):  # need to check

        result = int(destination_data, 2)
        result += 1;
        if (result >= 2 ** 16):
            result = result - 2 ** 16;
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (result >= (2 ** 15) or (result < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0
        flags['C'] = flags['C']
        return result

    def IncB(self, destination_data):  # need to check

        result = int(destination_data, 2)
        result += 1;
        if (result >= 2 ** 16):
            result = result - 2 ** 16;
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (result >= (2 ** 15) or (result < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0
        flags['C'] = flags['C']
        return result

    def Dec(self, destination_data):  # need to check
        result = int(destination_data, 2)
        if (result == 0):
            result = 2 ** 16;
        else:
            result = result - 1

        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (result >= (2 ** 15) or (result < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0
        flags['C'] = flags['C']
        return result

    def DecB(self, destination_data):  # need to check
        result = int(destination_data, 2)
        if (result == 0):
            result = 2 ** 16;
        else:
            result = result - 1

        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (result >= (2 ** 15) or (result < (-(2 ** 15)))):
            flags['V'] = 1
        else:
            flags['V'] = 0
        flags['C'] = flags['C']
        return result

    def Neg(self, destination_data):
        temp = int(destination_data, 2)
        result = -temp
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (destination_data == '1000000000000000'):
            flags['V'] = 1
        else:
            flags['V'] = 0
        if (result == 0):
            flags['C'] = 0
        else:
            flags['C'] = 1
        return result

    def NegB(self, destination_data):
        temp = int(destination_data, 2)
        result = -temp
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (destination_data == '1000000000000000'):
            flags['V'] = 1
        else:
            flags['V'] = 0
        if (result == 0):
            flags['C'] = 0
        else:
            flags['C'] = 1
        return result

    def Adc(self, destination_data):
        temp = int(destination_data, 2)
        carry = int(flags['C'])
        result = temp + carry
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp == 32767 and flags['C'] == 1):
            flags['V'] = 1
        else:
            flags['V'] = 0
        if (temp == 65535 and flags['C'] == 1):
            flags['C'] = 1
        else:
            flags['C'] = 0
        return result

    def AdcB(self, destination_data):
        temp = int(destination_data, 2)
        carry = int(flags['C'])
        result = temp + carry
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp == 32767 and flags['C'] == 1):
            flags['V'] = 1
        else:
            flags['V'] = 0
        if (temp == 65535 and flags['C'] == 1):
            flags['C'] = 1
        else:
            flags['C'] = 0
        return result

    def Sbc(self, destination_data):
        temp = int(destination_data, 2)
        carry = int(flags['C'])
        result = temp - carry
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp == 32768):
            flags['V'] = 1
        else:
            flags['V'] = 0
        if (temp == 0 and flags['C'] == 1):
            flags['C'] = 1
        else:
            flags['C'] = 0
        return result

    def SbcB(self, destination_data):
        temp = int(destination_data, 2)
        carry = int(flags['C'])
        result = temp - carry
        if (result < 0):
            flags['N'] = 1
        else:
            flags['N'] = 0
        if (result == 0):
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        if (temp == 32768):
            flags['V'] = 1
        else:
            flags['V'] = 0
        if (temp == 0 and flags['C'] == 1):
            flags['C'] = 1
        else:
            flags['C'] = 0
        return result

    ###################################################################

    def Tst(self, destination_data):
        flags['V'] = 0
        flags['C'] = 0
        temp = int(destination_data, 2)
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0

        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0

    def TstB(self, destination_data):
        flags['V'] = 0
        flags['C'] = 0
        temp = int(destination_data, 2)
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0

        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0

    def Ror(self, destination_data):
        temp_flag = str(flags['C'])
        flags['C'] = int(destination_data[15], 2)  # assume source_data is the destination
        temp = int((temp_flag + destination_data[:15]), 2)

        # temp = destination_data
        # higherbit = flags['C']
        # flags['C'] = int(temp[0], 2)
        # temp = str(higherbit) + temp[0:14]

        temp = int(temp, 2)
        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = flags['C'] ^ flags['N']
        return temp

    def RorB(self, destination_data):
        temp_flag = str(flags['C'])
        flags['C'] = int(destination_data[15], 2)  # assume source_data is the destination
        temp = int((temp_flag + destination_data[:15]), 2)

        # temp = destination_data
        # higherbit = flags['C']
        # flags['C'] = int(temp[0], 2)
        # temp = str(higherbit) + temp[0:14]

        temp = int(temp, 2)
        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = flags['C'] ^ flags['N']
        return temp

    def Rol(self, destination_data):

        temp_flag = str(flags['C'])
        flags['C'] = int(destination_data[0], 2)  # assume source_data is the destination
        temp = int((destination_data[1:] + temp_flag), 2)

        # lowerbit = flags['C']
        # temp = destination_data
        # flags['C'] = temp[15]
        # temp = temp << 1
        # temp[0] = lowerbit

        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = flags['C'] ^ flags['N']
        return temp

    def RolB(self, destination_data):

        temp_flag = str(flags['C'])
        flags['C'] = int(destination_data[0], 2)  # assume source_data is the destination
        temp = int((destination_data[1:] + temp_flag), 2)

        # lowerbit = flags['C']
        # temp = destination_data
        # flags['C'] = temp[15]
        # temp = temp << 1
        # temp[0] = lowerbit

        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = flags['C'] ^ flags['N']
        return temp

    def Asr(self, destination_data):
        flags['C'] = int(destination_data[15], 2)  # assume source_data is the destination
        temp = int((destination_data[0] + destination_data[:15]), 2)

        # temp = destination_data
        # flags['C'] = temp[0]  # assume source_data is the destination
        # higherbit = temp[15]
        # temp = temp >> 1
        # temp[15] = higherbit
        flags['V'] = flags['C'] ^ flags['N']
        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        return temp

    def AsrB(self, destination_data):
        flags['C'] = int(destination_data[15], 2)  # assume source_data is the destination
        temp = int((destination_data[0] + destination_data[:15]), 2)

        # temp = destination_data
        # flags['C'] = temp[0]  # assume source_data is the destination
        # higherbit = temp[15]
        # temp = temp >> 1
        # temp[15] = higherbit
        flags['V'] = flags['C'] ^ flags['N']
        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if temp == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        return temp

    def Asl(self, destination_data):
        flags['C'] = int(destination_data[0], 2)  # assume source_data is the destination
        temp = int((destination_data[1:] + '0'), 2)

        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if source_data == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = flags['C'] ^ flags['N']
        return temp

    def AslB(self, destination_data):
        flags['C'] = int(destination_data[0], 2)  # assume source_data is the destination
        temp = int((destination_data[1:] + '0'), 2)

        if temp < 0:
            flags['N'] = 1
        else:
            flags['N'] = 0
        if source_data == 0:
            flags['Z'] = 1
        else:
            flags['Z'] = 0
        flags['V'] = flags['C'] ^ flags['N']
        return temp

    def Sxt(self, destination_data):
        temp = destination_data
        if flags[N] == 1:
            temp = 65535
            flags['Z'] = 0
        else:
            temp = 0
            flags['Z'] = 1
        return temp

    ###### branch instructions ######

    def Br(self, destination_data):
        offset = destination_data
        if offset > 128:
            offset = 256 - offset
            return -offset
        else:
            return offset

    def Beq(self, destination_data):
        if flags['Z'] == 1:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bne(self, destination_data):
        if flags['Z'] == 0:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bpl(self, destination_data):
        if flags['N'] == 0:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bmi(self, destination_data):
        if flags['N'] == 1:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bvc(self, destination_data):
        if flags['V'] == 0:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bvs(self, destination_data):
        if flags['V'] == 1:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bhis(self, destination_data):
        if flags['C'] == 0:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    ################################################################################
    def Bcc(self, destination_data):
        if flags['C'] == 0:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Blo(self, destination_data):
        if flags['C'] == 1:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bcs(self, destination_data):
        if flags['C'] == 1:
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bge(self, destination_data):
        if ((flags['N'] ^ flags['V']) == 0):
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Blt(self, destination_data):
        if ((flags['N'] ^ flags['V']) == 1):
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bgt(self, destination_data):
        if ((flags['Z'] | (flags['N'] ^ flags['V'])) == 0):
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Ble(self, destination_data):
        if ((flags['Z'] | (flags['N'] ^ flags['V'])) == 1):
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Bhi(self, destination_data):
        if ((flags['C'] | flags['Z']) == 0):
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0

    def Blos(self, destination_data):
        if ((flags['C'] | flags['Z']) == 1):
            offset = destination_data
            if offset > 128:
                offset = 256 - offset
                return -offset
            else:
                return offset
        else:
            return 0


def Result_Conversion(result):
    if result < 0:
        result = result + 2 ** 16
    if result > 2 ** 16:
        result = result - 2 ** 16

    return result


if __name__ == "__main__":
    source = input("Input ascii file path")
    Debug = int(input("Choose Debug Mode: ON-1 OFF-0"),2)
    ReadFlag = 0
    loadInstr(source)
    if Debug:
        print('Initial flag status-->', flags)
        print('')
    while IR != '0000000000000000':
        IR = memory[R[7] + 1] + memory[R[7]]
        writeTrace(2, R[7])  ##write instruction fetch
        Count = Count + 1
        if IR == '0000000000000000':
            print('Execution Completed!')
            if Debug:
                print ('R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7', R[7],)
            print('Total number of Instructions executed :', Count)
            # print('Total number of Memory reads :', #rcount)
            # print('Total number of Memory writes:', #wcount)
            tracefile.close()
            break
        R[7] += 2
        instruction_type = decode(IR)

        obj_Addressing_Modes = Addressing_Modes()
        obj_Operation = Operation()
        Reg_Flag = 0
        ReadFlag = 0

        if Debug:
            print ('R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7', R[7],)

        if (instruction_type == 'double_operand'):
            source_reg_number = int((instruction['source_reg']), 2)
            Src_flag = 1;
            obj_Addressing_Modes.set_Addressing_Mode(instruction['source_mode'], source_reg_number, 0)
            source_data = int((obj_Addressing_Modes.Data), 2)
            Src_flag = 0;
            ##writetrace-check
            # if ReadFlag == 1:
            #   writeTrace(0, obj_Addressing_Modes.Address)
            #  ReadFlag = 0
            if source_data >= 2 ** 15:
                source_data = (source_data - (2 ** 16))

            destination_reg_number = int((instruction['destination_reg']), 2)
            obj_Addressing_Modes.set_Addressing_Mode(instruction['destination_mode'], destination_reg_number, 0)
            destination_data = int((obj_Addressing_Modes.Data), 2)
            ##writetrace-check
            # if (ReadFlag == 1):
            #  writeTrace(0, obj_Addressing_Modes.Address)
            #  ReadFlag = 0
            if destination_data >= 2 ** 15:
                destination_data = (destination_data - (2 ** 16))

            if instruction['destination_mode'] != '000':
                destination_address = obj_Addressing_Modes.Address
            else:
                destination_address = destination_reg_number
                Reg_Flag = 1

            if Debug:
                print ('source data', source_data)
                print ('dest_data-->', destination_data, 'dest_addr-->', destination_address)

            ##if (instruction['source_mode'] == '000'):
            if Reg_Flag:
                result = obj_Operation.set_Operation(instruction['opcode'], source_data, destination_data)
                if result != None:
                    result = Result_Conversion(result)
                    R[destination_address] = result
                    if Debug:
                        print('Reg', destination_address, '-->', R[destination_address])
            else:
                result = obj_Operation.set_Operation(instruction['opcode'], source_data, destination_data)

                if result != None:
                    result = Result_Conversion(result)
                    result = bin(result)[2:].zfill(16)
                    memory[destination_address] = result[8:]
                    memory[destination_address + 1] = result[:8]
                    ##writetrace-check
                    if (instruction['opcode'] == '110'):
                        writeTrace(0, destination_address)
                        # rcount+=1
                    writeTrace(1, destination_address)
                    # wcount+=1
                    ReadFlag = 0
                    if Debug:
                        print(
                        destination_address + 1, '-->', memory[destination_address + 1], '.....', destination_address,
                        '-->', memory[destination_address])
            if Debug:
                print('flag status-->', flags)
                print (
                    'After--''R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7',
                    R[7],)
                print('The above all statements are for IR-->', int(IR, 2))
                print('Double operand executed\n')

        elif (instruction_type == 'single_operand'):
            destination_reg_number = int((instruction['destination_reg']), 2)
            obj_Addressing_Modes.set_Addressing_Mode(instruction['destination_mode'], destination_reg_number, 0)
            destination_data = obj_Addressing_Modes.Data
            ##writetrace-check
            # if ReadFlag == 1:
            #   writeTrace(0, obj_Addressing_Modes.Address)
            #   ReadFlag = 0

            if instruction['destination_mode'] != '000':
                destination_address = obj_Addressing_Modes.Address
            else:
                destination_address = destination_reg_number
                Reg_Flag = 1
            if IR[:7] == '0000100':
                obj_Operation.set_Operation(instruction['opcode'], 0, destination_data)
                R[7] = destination_address
            else:
                if Reg_Flag:
                    result = obj_Operation.set_Operation(instruction['opcode'], source_data, destination_data)
                    if result != None:
                        result = Result_Conversion(result)
                        R[destination_address] = result
                        if Debug:
                            print('Reg', destination_address, '-->', R[destination_address])
                else:
                    result = obj_Operation.set_Operation(instruction['opcode'], source_data, destination_data)
                    if result != None:
                        result = Result_Conversion(result)
                        result = bin(result)[2:].zfill(16)
                        memory[destination_address] = result[8:]
                        memory[destination_address + 1] = result[:8]
                        ##writetrace-check
                        writeTrace(1, destination_address)
                        # wcount+=1
                        ReadFlag = 0
                        if Debug:
                            print(destination_address + 1, '-->', memory[destination_address + 1], '.....',
                                  destination_address,
                                  '-->', memory[destination_address])
            if Debug:
                print('flag status-->', flags)
                print (
                    'After--''R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7',
                    R[7],)
                print('The above all statements are for IR-->', int(IR, 2))
                print('Single operand executed\n')

        elif (instruction_type == 'branch'):
            destination_data = int((instruction['offset']), 2)
            ##writetrace-check
            # if ReadFlag == 1:
            #   writeTrace(0, obj_Addressing_Modes.Address)
            #   ReadFlag = 0

            result = obj_Operation.set_Operation(instruction['opcode'], 0, destination_data)
            R[7] += (result * 2)
            # if R[7]<-128:
            #   R[7] = 256 + R[7]
            # elif R[7]>127:
            #   R[7] = 128 - R[7]

            if Debug:
                print('flag status-->', flags)
                print (
                    'After--''R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7',
                    R[7],)
                print('The above all statements are for IR-->', int(IR, 2))
                print('Jump Executed\n')

        elif (instruction_type == 'psw'):
            obj_Operation.set_Operation(instruction['opcode'], 0, destination_data)
            if Debug:
                print('flag status-->', flags)
                print (
                    'After--''R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7',
                    R[7],)
                print('The above all statements are for IR-->', int(IR, 2))
                print('PSW Executed\n')

        elif (instruction_type == 'swab'):
            destination_reg_number = int((instruction['destination_reg']), 2)
            obj_Addressing_Modes.set_Addressing_Mode(instruction['destination_mode'], destination_reg_number, 0)
            destination_data = obj_Addressing_Modes.Data
            ##writetrace-check
            # if ReadFlag == 1:
            #   writeTrace(0, obj_Addressing_Modes.Address)
            #  ReadFlag = 0
            if int(destination_data, 2) >= 2 ** 15:
                destination_data = int(destination_data, 2) - (2 ** 16)

            if instruction['destination_mode'] != '000':
                destination_address = obj_Addressing_Modes.Address
            else:
                destination_address = destination_reg_number
                Reg_Flag = 1

            if Debug:
                print ('source data', source_data)
                print ('dest_data-->', destination_data, 'dest_addr-->', destination_address)

            ##if (instruction['source_mode'] == '000'):
            if Reg_Flag:
                result = obj_Operation.set_Operation(instruction['opcode'], source_data, destination_data)
                if result != None:
                    result = Result_Conversion(result)
                    R[destination_address] = result
                    if Debug:
                        print('Reg', destination_address, '-->', R[destination_address])
            else:
                result = obj_Operation.set_Operation(instruction['opcode'], source_data, destination_data)
                if result != None:
                    result = Result_Conversion(result)
                    result = bin(result)[2:].zfill(16)
                    memory[destination_address] = result[8:]
                    memory[destination_address + 1] = result[:8]
                    ##writetrace-check
                    writeTrace(1, destination_address)
                    # wcount+=1
                    #  ReadFlag = 0
                    if Debug:
                        print(
                        destination_address + 1, '-->', memory[destination_address + 1], '.....', destination_address,
                        '-->', memory[destination_address])
            if Debug:
                print('flag status-->', flags)
                print (
                    'After--''R0', R[0], 'R1', R[1], 'R2', R[2], 'R3', R[3], 'R4', R[4], 'R5', R[5], 'R6', R[6], 'R7',
                    R[7],)
                print('The above all statements are for IR-->', int(IR, 2))
                print('SWAB executed\n')
        elif instruction_type == 'RTS':
            # writeTrace(1, R[7] - 2)
            R[7] = R[int((instruction['destination_reg']), 2)]
            R[5] = int((memory[R[6] + 1] + memory[R[6]]), 2)
            writeTrace(0, R[6])
            # rcount+=1
            R[6] = R[6] + 2
        source_data = None
        destination_data = None
