def parse_riscv(file):
    with open(file, encoding = "utf-8") as f:
        header = f.readline()
        header_tokens = header.split(sep=None)
        asm_type = header_tokens[0]
        start_addr = header_tokens[1]
        if len(header_tokens) > 2:
            compressed = header_tokens[2] == 'C'
        else:
            compressed = False
        # Python 3.10!
        match asm_type:
            case "#disas":
                # Disassembly
                code = dict()
                for asm in f:
                    tokens = asm.split(sep=None)
                    if len(tokens) == 0:
                        continue
                    if tokens[0][-1] == ':':
                        addr = tokens[0][:-1]
                        op = tokens[2]
                        if len(tokens) > 3:
                            raw = op + ' ' + tokens[3]
                        else:
                            raw = op
                        instr = {
                            'op': op,  # Operation
                            'size': 2 if compressed and len(tokens[1]) == 4 else 4, # Compressed?
                            'raw': raw # For displaying
                        }
                        match op:
                            case 'jal':
                                # Parse jump
                                instr_args = tokens[3].split(sep=',')
                                instr['rd'] = instr_args[0]
                                instr['i'] = instr_args[1]
                            case 'j':
                                # Jump pseudoinstruction
                                instr['rd'] = 'ra'
                                instr['i'] = tokens[3]
                            case 'beq' | 'bne' | 'blt' | 'bltu' | 'bge' | 'bgeu':
                                instr_args = tokens[3].split(sep=',')
                                instr['rs1'] = instr_args[0]
                                instr['rs2'] = instr_args[1]
                                instr['i'] = instr_args[2]
                            case 'bnez' | 'beqz':
                                instr_args = tokens[3].split(sep=',')
                                instr['rs1'] = instr_args[0]
                                instr['rs2'] = 'zero'
                                instr['i'] = instr_args[1]
                            case 'li':
                                instr_args = tokens[3].split(sep=',')
                                instr['rs1'] = instr_args[0]
                                instr['i'] = int(instr_args[1])
                            case 'addi':
                                instr_args = tokens[3].split(sep=',')
                                instr['rd'] = instr_args[0]
                                instr['rs1'] = instr_args[1]
                                instr['i'] = int(instr_args[2])
                        code[addr] = instr
                return (int(start_addr, 16), code)
            case _:
                return None
