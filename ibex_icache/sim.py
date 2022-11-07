from .parse_asm import parse_riscv
import pandas as pd

class RegFile:
    def __init__(self):
        # No Floating point
        self.regs = {
            'zero': 0,
            'ra': 0,
            'sp': 0,
            'gp': 0,
            'tp': 0,
            't0': 0,
            't1': 0,
            't2': 0,
            't3': 0,
            't4': 0,
            't5': 0,
            't6': 0,
            's0': 0,
            's1': 0,
            's2': 0,
            's3': 0,
            's4': 0,
            's5': 0,
            's6': 0,
            's7': 0,
            's8': 0,
            's9': 0,
            's10': 0,
            's11': 0,
            'a0': 0,
            'a1': 0,
            'a2': 0,
            'a3': 0,
            'a4': 0,
            'a5': 0,
            'a6': 0,
            'a7': 0
        }
    
    def getreg(self, reg):
        if reg == 'fp':
            return self.regs['s0']
        else:
            return self.regs[reg]

    def setreg(self, reg, val):
        if reg == 'fp':
            self.regs['s0'] = val
        elif reg == 'zero':
            return
        else:
            self.regs[reg] = val

class ICacheSim:
    def __init__(self):
        # Simulation registers
        self.regs = RegFile()

    def load_instr(self, file):
        (self.start_addr, self.instrs) = parse_riscv(file)
        self.result = dict()
        self.result['data'] = dict()
        for addr, instr in self.instrs.items():
            self.result['data'][addr] = {
                'instr': instr['op'],
                'hits': 0,
                'misses': 0,
            }
            
    def print_instr(self):
        print(self.start_addr)
        print(self.instrs)
    
    def print_result(self):
        # There should be a better way to do this but *shrug*
        raw_data = [(addr, i['instr'], i['hits'], i['misses']) for (addr, i) in self.result['data'].items()]
        f_row_hd = [""] * len(raw_data)
        f_addr = []
        f_instr = []
        f_hits = []
        f_misses = []
        for addr, instr, hits, misses in raw_data:
            f_addr.append(addr)
            f_instr.append(instr)
            f_hits.append(hits)
            f_misses.append(misses)
        f_row_hd.append('Total')
        f_addr.append('')
        f_instr.append('')
        f_hits.append(sum(f_hits))
        f_misses.append(sum(f_misses))
        d = {
            '': f_row_hd,
            'Address': f_addr,
            'Instruction': f_instr,
            'Hits': f_hits,
            'Misses': f_misses
        }
        df = pd.DataFrame(data=d)
        print(df.to_string(index=False))
        print('Hit rate: {0:.2f}%'.format(100 * f_hits[-1] / self.result['instrs_ret']))
        print('Instructions run: {0}'.format(self.result['instrs_ret']))

    def sim(self, cache, max_instrs):
        """Simulate instruction accesses with the cache."""
        if f'{self.start_addr:x}' not in self.instrs:
            raise Exception(f'Could not find start instruction at 0x{self.start_addr:x}')
        else:
            # Simulation Initialization
            pc = self.start_addr # Program Counter
            instrs_ret = 0
            # Simulation loop
            while instrs_ret < max_instrs:
                pc_key = f'{pc:x}'
                if pc_key not in self.instrs:
                    print(f'Could not find instruction at address 0x{pc:x}! Ending sim...')
                    break
                # Cache stats
                if cache.is_hit(pc):
                    self.result['data'][pc_key]['hits'] += 1
                else:
                    cache.evict_and_alloc(pc)
                    self.result['data'][pc_key]['misses'] += 1
                # Instruction handling
                instr = self.instrs[pc_key]
                match instr['op']:
                    case 'jal' | 'j':
                        self.regs.setreg(instr['rd'], pc + 4)
                        pc = int(instr['i'], 16)
                    case 'bne' | 'bnez':
                        rs1 = self.regs.getreg(instr['rs1'])
                        rs2 = self.regs.getreg(instr['rs2'])
                        if rs1 != rs2:
                            pc = int(instr['i'], 16)
                        else:
                            pc += 4
                    case 'beq' | 'beqz':
                        rs1 = self.regs.getreg(instr['rs1'])
                        rs2 = self.regs.getreg(instr['rs2'])
                        if rs1 == rs2:
                            pc = int(instr['i'], 16)
                        else:
                            pc += 4
                    case 'blt' | 'bltu': 
                        rs1 = self.regs.getreg(instr['rs1'])
                        rs2 = self.regs.getreg(instr['rs2'])
                        if rs1 < rs2:
                            pc = int(instr['i'], 16)
                        else:
                            pc += 4
                    case 'bge' | 'bgeu':
                        rs1 = self.regs.getreg(instr['rs1'])
                        rs2 = self.regs.getreg(instr['rs2'])
                        if rs1 <= rs2:
                            pc = int(instr['i'], 16)
                        else:
                            pc += 4
                    case 'li':
                        self.regs.setreg(instr['rs1'], instr['i'])
                        pc += 4
                    case 'addi':
                        rs1 = self.regs.getreg(instr['rs1'])
                        imm = instr['i']
                        self.regs.setreg(instr['rd'], rs1 + imm)
                        pc += 4
                    case 'ret':
                        pc = self.regs.getreg('ra')
                    case _:
                        pc += 4
                instrs_ret += 1
            self.result['instrs_ret'] = instrs_ret
