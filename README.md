# Ibex Core I-Cache Simulation

This repo contains a very simple cache simulator for the Ibex Core by lowRISC to
model cache hits/misses. It is NOT a 100% accurate model! In particular, cache
eviction cannot be simulated without dramatically increasing the complexity, and
you might as well simulate the whole system at that point.

Details: Cache eviction is partially based off a pseudorandom generator, which
is implemented by a simple round-robin, 1-hot signal that updates every cycle.
This would require simulating core cycles, and you'd be better off using a tool
like Verilator to simulate the system.

## Requirements
* Python 3.10+
* pandas 1.5+

## Usage
See below for explicit examples.
```python
from ibex_icache.icache import CacheConfiguration, IbexICache
from ibex_icache.sim import ICacheSim
```

First, create a cache configuration with size (bytes), # of ways, and line size
(bytes):
```python
# Default configuration
cache_config = CacheConfiguration(size = 4096, ways = 2, line_size = 8)
```

Next, instantiate the cache. This takes in instruction width (always 32) and the
cache config.
```python
cache = IbexICache(32, cache_config)
```

Instantiate the cache simulation instance.
```python
cache_sim = ICacheSim()
```

Load RISC-V instructions from a file. The file must have a header formatted like
so:
```
#disas <start_addr>
```
The `#disas` indicates to the parser that the file comes from a disassembler,
and `<start_addr>` is where the simulator will initially set the program
counter. Currently, the parser and simulation only works with noncompressed
instructions.

Supported instructions so far:
```
jal, j
bne, bnez
beq, beqz
blt, bltu
bge, bgez
li
addi
```
**NOTE**: For now, signed and unsigned operations are treated as signed. 

Load the instructions:
```
cache_sim.load_instr("sample.lst")
```

Simulate the cache. It takes in a cache instance and an integer to specify the max
number of dynamic instructions to execute.
```python
# Max of 100 instructions can be retired at runtime
cache_sim.sim(cache, 100)
```

Finally, print the results.
```python
cache_sim.print_result()
```

## Samples
The `test` folder has some working samples. In `test/asm` there are a few sample
diassemblies to try. Running
```python
python3 branch.py
```
should yield something like the following:
```bash
tkng:~$ python3 branch.py
Could not find instruction at address 0x1013d4! Ending sim...
      Address Instruction  Hits  Misses
       1013c4          li     0       1
       1013c8        addi    15       1
       1013cc         jal    16       0
       1013d0        bnez    15       1
       101368         nop    15       1
       10136c         ret    16       0
Total                        77       4
Hit rate: 95.06%
Instructions run: 81
```
