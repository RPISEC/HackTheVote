from binaryninja import *

CODE_BASE = 0x100000
GST_BASE = 0x200000
GFT_BASE = 0x300000
FST_BASE = 0x400000
FFT_BASE = 0x500000
LBP_BASE = 0x600000
ADDR_MASK = 0xFFFFF

class OpCode(enum.IntEnum):
    FuncDecl = 0
    CreateObject = 1
    Nop2 = 2
    Nop3 = 3
    AddObject = 4
    EndObject = 5
    JmpIfFNot = 6
    JmpIfNot = 7
    JmpIfF = 8
    JmpIf = 9
    JmpIfNotNp = 10
    JmpIfNp = 11
    Jmp = 12
    Return = 13
    CmpEq = 14
    CmpGr = 15
    CmpGe = 16
    CmpLt = 17
    CmpLe = 18
    CmpNe = 19
    Xor = 20
    Mod = 21
    BitAnd = 22
    BitOr = 23
    Not = 24
    NotF = 25
    OnesComplement = 26
    Shr = 27
    Shl = 28
    And = 29
    Or = 30
    Add = 31
    Sub = 32
    Mul = 33
    Div = 34
    Neg = 35
    SetCurVar = 36
    SetCurVarCreate = 37
    SetCurVarArray = 38
    SetCurVarArrayCreate = 39
    LoadVarUInt = 40
    LoadVarFlt = 41
    LoadVarStr = 42
    SaveVarUInt = 43
    SaveVarFlt = 44
    SaveVarStr = 45
    SetCurObject = 46
    SetCurObjectNew = 47
    SetCurField = 48
    SetCurFieldArray = 49
    LoadFieldUInt = 50
    LoadFieldFlt = 51
    LoadFieldStr = 52
    SaveFieldUInt = 53
    SaveFieldFlt = 54
    SaveFieldStr = 55
    StrToUInt = 56
    StrToFlt = 57
    StrToNone = 58
    FltToUint = 59
    FltToStr = 60
    FltToNone = 61
    UIntToFlt = 62
    UIntToStr = 63
    UIntToNone = 64
    LoadImmedUInt = 65
    LoadImmedFlt = 66
    TagToStr = 67
    LoadImmedStr = 68
    LoadImmedIdent = 69
    CallFuncResolve = 70
    CallFunc = 71
    Nop72 = 72
    AdvanceStr = 73
    AdvanceStrAppendChar = 74
    AdvanceStrComma = 75
    AdvanceStrNul = 76
    RewindStr = 77
    TerminateRewindStr = 78
    CompareStr = 79
    Push = 80
    PushFrame = 81
    Break = 82
    Invalid = 83


def ip_to_addr(ip):
    return CODE_BASE + (ip * 4)


def addr_to_ip(addr):
    return (addr - CODE_BASE) // 4


def str_to_addr(str_offset, is_global):
    global GST_BASE, FST_BASE
    if is_global:
        return GST_BASE + str_offset - 1 if str_offset != 0 else 0
    else:
        return FST_BASE + str_offset - 1 if str_offset != 0 else 0


class TSArch(Architecture):
    name = "TS"
    address_size = 4
    default_int_size = 4
    instr_alignment = 1
    max_instr_length = 25 + 32 * 4
    regs = {
        "sp": RegisterInfo("sp", 4)
    }
    stack_pointer = "sp"
    flags = []
    flag_write_types = []
    flag_roles = {}
    flags_required_for_flag_condition = {}
    flags_written_by_flag_write_type = {}

    def get_instruction_info(self, data, addr):
        ins_info, tokens = TSArch.decode_ins(data, addr)
        return ins_info

    @staticmethod
    def decode_ins(data, addr):
        DECODERS = {
            OpCode.FuncDecl: TSArch.decode_func_decl,
            OpCode.CreateObject: TSArch.decode_create_object,
            OpCode.AddObject: TSArch.decode_register_object,
            OpCode.EndObject: TSArch.decode_register_object,
            OpCode.JmpIfFNot: TSArch.decode_jmp,
            OpCode.JmpIfNot: TSArch.decode_jmp,
            OpCode.JmpIfF: TSArch.decode_jmp,
            OpCode.JmpIf: TSArch.decode_jmp,
            OpCode.JmpIfNotNp: TSArch.decode_jmp,
            OpCode.JmpIfNp: TSArch.decode_jmp,
            OpCode.Jmp: TSArch.decode_jmp,
            OpCode.Return: TSArch.decode_return,
            OpCode.SetCurVar: TSArch.decode_identifier,
            OpCode.SetCurVarCreate: TSArch.decode_identifier,
            OpCode.SetCurField: TSArch.decode_identifier,
            OpCode.LoadImmedIdent: TSArch.decode_identifier,
            OpCode.LoadImmedUInt: TSArch.decode_load_immed_uint,
            OpCode.LoadImmedFlt: TSArch.decode_load_immed_flt,
            OpCode.TagToStr: TSArch.decode_load_immed_str,
            OpCode.LoadImmedStr: TSArch.decode_load_immed_str,
            OpCode.CallFuncResolve: TSArch.decode_call_func,
            OpCode.CallFunc: TSArch.decode_call_func,
            OpCode.AdvanceStrAppendChar: TSArch.decode_advance_str_append_char,
        }
        info = InstructionInfo()

        ins_length = 0
        ins_length, info.op = TSArch.read_int(data, ins_length)
        if OpCode(info.op) in DECODERS:
            ins_length, tokens = DECODERS[OpCode(info.op)](data, addr, ins_length, info)
        else:
            tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name)]
        info.length = ins_length

        return info, tokens

    @staticmethod
    def decode_func_decl(data, addr, ins_length, info):
        ins_length, info.name_index = TSArch.read_int(data, ins_length)
        ins_length, info.namespace_name_index = TSArch.read_int(data, ins_length)
        ins_length, info.package_name_index = TSArch.read_int(data, ins_length)
        ins_length, info.has_body = TSArch.read_int(data, ins_length)
        ins_length, info.next_ip = TSArch.read_int(data, ins_length)
        ins_length, info.argc = TSArch.read_int(data, ins_length)

        info.args = []
        for _ in range(info.argc):
            ins_length, index = TSArch.read_int(data, ins_length)
            info.args.append(index)

        info.target_ip = addr_to_ip(addr) + 7 + info.argc

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "["),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"str_{str_to_addr(info.package_name_index, True):x}", value=str_to_addr(info.package_name_index, True), address=str_to_addr(info.package_name_index, True)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "] "),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"str_{str_to_addr(info.namespace_name_index, True):x}", value=str_to_addr(info.namespace_name_index, True), address=str_to_addr(info.namespace_name_index, True)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "::"),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"str_{str_to_addr(info.name_index, True):x}", value=str_to_addr(info.name_index, True), address=str_to_addr(info.name_index, True)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "() @ "),
                  InstructionTextToken(InstructionTextTokenType.CodeSymbolToken, f"{ip_to_addr(info.target_ip):x}", value=ip_to_addr(info.target_ip), address=ip_to_addr(info.target_ip)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, " args: [")]
        for i, arg in enumerate(info.args):
            if i > 0:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))
            tokens.append(InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"str_{str_to_addr(arg, True):x}", value=str_to_addr(arg, True), address=str_to_addr(arg, True)))
        tokens.extend([
                  InstructionTextToken(InstructionTextTokenType.TextToken, "]"),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")])

        info.add_branch(BranchType.UnconditionalBranch, ip_to_addr(info.next_ip))
        info.add_branch(BranchType.CallDestination, ip_to_addr(info.target_ip))

        return ins_length, tokens

    @staticmethod
    def decode_create_object(data, addr, ins_length, info):
        ins_length, info.parent_name_index = TSArch.read_int(data, ins_length)
        ins_length, info.is_data_block = TSArch.read_int(data, ins_length)
        ins_length, info.fail_ip = TSArch.read_int(data, ins_length)

        info.target_ip = addr_to_ip(addr) + 4

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.CodeSymbolToken, f"obj_{ip_to_addr(info.target_ip):x}", value=ip_to_addr(info.target_ip), address=ip_to_addr(info.target_ip)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        info.add_branch(BranchType.UnconditionalBranch, ip_to_addr(info.fail_ip))
        info.add_branch(BranchType.CallDestination, ip_to_addr(info.target_ip))
        return ins_length, tokens

    @staticmethod
    def decode_register_object(data, addr, ins_length, info):
        ins_length, info.place_at_root = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.TextToken, f"root: {info.place_at_root}"),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_jmp(data, addr, ins_length, info):
        ins_length, info.target_ip = TSArch.read_int(data, ins_length)
        info.next_ip = addr_to_ip(addr) + 2

        if info.op == OpCode.JmpIfFNot or info.op == OpCode.JmpIfNot or info.op == OpCode.JmpIfF or info.op == OpCode.JmpIf or info.op == OpCode.JmpIfNotNp or info.op == OpCode.JmpIfNp:
            info.add_branch(BranchType.TrueBranch, ip_to_addr(info.target_ip))
            info.add_branch(BranchType.FalseBranch, ip_to_addr(info.next_ip))
        if info.op == OpCode.Jmp:
            info.add_branch(BranchType.UnconditionalBranch, ip_to_addr(info.next_ip))

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.AddressDisplayToken, f"{ip_to_addr(info.target_ip):x}", value=ip_to_addr(info.next_ip), address=ip_to_addr(info.next_ip)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_return(data, addr, ins_length, info):
        info.add_branch(BranchType.FunctionReturn)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name)]

        return ins_length, tokens

    @staticmethod
    def decode_identifier(data, addr, ins_length, info):
        ins_length, info.name_index = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"{str_to_addr(info.name_index, True):x}", value=str_to_addr(info.name_index, True), address=str_to_addr(info.name_index, True)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_load_immed_uint(data, addr, ins_length, info):
        ins_length, info.value = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.value:x}", value=info.value),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_load_immed_flt(data, addr, ins_length, info):
        ins_length, info.float_index = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.TextToken, f"{info.float_index:x}"),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_load_immed_str(data, addr, ins_length, info):
        ins_length, info.string_offset = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.TextToken, f"{info.string_offset:x}"),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_call_func(data, addr, ins_length, info):
        ins_length, info.name_index = TSArch.read_int(data, ins_length)
        ins_length, info.namespace_index = TSArch.read_int(data, ins_length)
        ins_length, info.call_type = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"str_{str_to_addr(info.namespace_index, True):x}", value=str_to_addr(info.namespace_index, True), address=str_to_addr(info.namespace_index, True)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "::"),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"str_{str_to_addr(info.name_index, True):x}", value=str_to_addr(info.name_index, True), address=str_to_addr(info.name_index, True)),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "//"),
                  InstructionTextToken(InstructionTextTokenType.DataSymbolToken, f"{info.call_type}"),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def decode_advance_str_append_char(data, addr, ins_length, info):
        ins_length, info.char = TSArch.read_int(data, ins_length)

        tokens = [InstructionTextToken(InstructionTextTokenType.InstructionToken, OpCode(info.op).name),
                  InstructionTextToken(InstructionTextTokenType.TextToken, "("),
                  InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.char}", value=info.char),
                  InstructionTextToken(InstructionTextTokenType.TextToken, ")")]

        return ins_length, tokens

    @staticmethod
    def read_int(data, ins_length):
        return ins_length + 4, struct.unpack("<I", data[ins_length:ins_length+4])[0]

    def get_instruction_text(self, data, addr):
        info, tokens = self.decode_ins(data, addr)

        return tokens, info.length

    def get_instruction_low_level_il(self, data, addr, il: LowLevelILFunction):
        return None
        # Not really feasible without bv as a param
        # info, tokens = self.decode_ins(data, addr)
        # if OpCode(info.op) == OpCode.FuncDecl:
        #     return info.length
        # elif OpCode(info.op) == OpCode.LoadImmedFlt:
        #     il.append(il.push(4, il.const(4, info.float_index)))
        # elif OpCode(info.op) == OpCode.FltToNone:
        #     il.append(il.pop(4))
        # elif OpCode(info.op) == OpCode.Add:
        #     il.append(il.push(4, il.float_add(4, il.pop(4), il.pop(4))))
        # elif OpCode(info.op) == OpCode.Sub:
        #     il.append(il.push(4, il.float_sub(4, il.pop(4), il.pop(4))))
        # elif OpCode(info.op) == OpCode.Mul:
        #     il.append(il.push(4, il.float_mult(4, il.pop(4), il.pop(4))))
        # elif OpCode(info.op) == OpCode.Div:
        #     il.append(il.push(4, il.float_Div(4, il.pop(4), il.pop(4))))
        # else:

    def is_never_branch_patch_available(self, data, addr):
        return False

    def is_always_branch_patch_available(self, data, addr):
        return False

    def is_invert_branch_patch_available(self, data, addr):
        return False

    def is_skip_and_return_zero_patch_available(self, data, addr):
        return False

    def is_skip_and_return_value_patch_available(self, data, addr):
        return False

    # def convert_to_nop(self, data, addr):
    #     pass

    # def always_branch(self, data, addr):
    #     pass

    # def invert_branch(self, data, addr):
    #     pass

    # def skip_and_return_value(self, data, addr, value):
    #     pass


class DSOView(BinaryView):
    name = 'DSO'
    long_name = "DSO Binary View"

    def __init__(self, data):
        BinaryView.__init__(self, file_metadata=data.file, parent_view=data)
        self.loader = None
        self.arch = Architecture['TS']
        self.platform = Architecture["TS"].standalone_platform
        self.raw = data

    @classmethod
    def is_valid_for_data(self, data):
        rdr = BinaryReader(data)
        version = rdr.read32le()
        if version != 33 and version != 36:
            return False
        return True

    def read_string_table(self, rdr, size, base):
        string_table_end = rdr.offset + size
        while rdr.offset < string_table_end:
            str_addr = rdr.offset
            str_len = 0
            while rdr.read8() != 0 and rdr.offset < string_table_end:
                str_len += 1
            self.define_data_var(str_addr + base, Type.array(Type.char(), str_len + 1))

    def read_float_table(self, rdr, size, base):
        for _ in range(size):
            self.define_data_var(rdr.offset + base, Type.float(8))
            rdr.read64()

    def define_int4_symbol(self, addr, name):
        self.define_data_var(addr, Type.int(4))
        self.define_auto_symbol(Symbol(SymbolType.DataSymbol, addr, name))

    def add_seg_sec(self, name, vbase, fbase, length, flags, semantics):
        self.add_auto_segment(vbase, length, fbase, length, flags)
        self.add_auto_section(name, vbase, length, semantics)

    def init(self):
        rdr = BinaryReader(self.parent_view)
        self.version = rdr.read32le()

        string_table_size = rdr.read32le()
        if string_table_size > 0:
            self.add_seg_sec("Global Strings", GST_BASE, rdr.offset, string_table_size, SegmentFlag.SegmentReadable, SectionSemantics.ReadOnlyDataSectionSemantics)
            self.read_string_table(rdr, string_table_size, GST_BASE - rdr.offset)

        float_table_size = rdr.read32le()
        if float_table_size > 0:
            self.add_seg_sec("Global Floats", GFT_BASE, rdr.offset, float_table_size * 8, SegmentFlag.SegmentReadable, SectionSemantics.ReadOnlyDataSectionSemantics)
            self.read_float_table(rdr, float_table_size, GFT_BASE - rdr.offset)

        string_table_size = rdr.read32le()
        if string_table_size > 0:
            self.add_seg_sec("Function Strings", FST_BASE, rdr.offset, string_table_size, SegmentFlag.SegmentReadable, SectionSemantics.ReadOnlyDataSectionSemantics)
            self.read_string_table(rdr, string_table_size, FST_BASE - rdr.offset)

        float_table_size = rdr.read32le()
        if float_table_size > 0:
            self.add_seg_sec("Function Floats", FFT_BASE, rdr.offset, float_table_size * 8, SegmentFlag.SegmentReadable, SectionSemantics.ReadOnlyDataSectionSemantics)
            self.read_float_table(rdr, float_table_size, FFT_BASE - rdr.offset)

        opcount = rdr.read32le()
        line_break_pair_count = rdr.read32le()

        # Parse ops
        ops_start = rdr.offset
        for i in range(opcount):
            if rdr.read8() == 0xff:
                self.parent_view.remove(rdr.offset - 1, 1)
                rdr.seek_relative(-1)
                rdr.read32()
            else:
                self.parent_view.insert(rdr.offset, b'\x00\x00\x00')
                rdr.seek_relative(3)

        if opcount > 0:
            self.add_seg_sec("Code", CODE_BASE, ops_start, opcount * 4, SegmentFlag.SegmentReadable | SegmentFlag.SegmentExecutable, SectionSemantics.ReadOnlyCodeSectionSemantics)

        if line_break_pair_count > 0:
            self.add_seg_sec("Line Break Pairs", LBP_BASE, rdr.offset, line_break_pair_count * 8, SegmentFlag.SegmentReadable, SectionSemantics.ReadOnlyDataSectionSemantics)
            rdr.seek_relative(line_break_pair_count * 8)

        gidents = rdr.read32le()
        for _0 in range(gidents):
            string_offset = rdr.read32le()
            ref_count = rdr.read32le()

            for _1 in range(ref_count):
                code_offset = rdr.read32le()
                self.parent_view.write(ops_start + code_offset * 4, struct.pack("<I", string_offset + 1))

        if opcount > 0:
            self.define_auto_symbol(Symbol(SymbolType.FunctionSymbol, CODE_BASE, "_main"))
            self.add_function(CODE_BASE, self.platform)
            self.add_analysis_completion_event(self.find_functions)
        return True

    def find_functions(self):
        main_fn = self.get_function_at(CODE_BASE)
        for (tokens, addr) in main_fn.instructions:
            data = self[addr:addr + self.arch.max_instr_length]
            info, _ = TSArch.decode_ins(data, addr)

            if hasattr(info, 'op'):
                if OpCode(info.op) == OpCode.FuncDecl:
                    name_index = info.name_index
                    namespace_name_index = info.namespace_name_index
                    package_name_index = info.package_name_index

                    name_str = self.get_string(name_index, True)
                    namespace_name_str = self.get_string(namespace_name_index, True)
                    package_name_str = self.get_string(package_name_index, True)

                    name = ""
                    if package_name_index != 0:
                        name += f"[{package_name_str}] "
                    if namespace_name_index != 0:
                        name += f"{namespace_name_str}::"
                    name += f"{name_str}"

                    self.add_function(ip_to_addr(info.target_ip))
                    self.define_auto_symbol(Symbol(SymbolType.FunctionSymbol, ip_to_addr(info.target_ip), name))

        for fn in self.functions:
            refs = self.get_code_refs(fn.lowest_address)
            ref: ReferenceSource
            for ref in refs:
                data = self[ref.address:ref.address + self.arch.max_instr_length]
                info, _ = TSArch.decode_ins(data, ref.address)
                if hasattr(info, 'op'):
                    if OpCode(info.op) == OpCode.CreateObject:
                        self.define_auto_symbol(Symbol(SymbolType.FunctionSymbol, ref.address, f"newObject_{addr_to_ip(ref.address)}"))


    def get_string(self, index, is_gst):
        return self.get_ascii_string_at((GST_BASE if is_gst else FST_BASE) + index - 1) if index > 0 else ""

    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return 0


DSOView.register()
TSArch.register()
