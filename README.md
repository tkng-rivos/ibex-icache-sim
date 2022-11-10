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
tkng: ~/ibex_icache_sim/test$ python3 branch.py
Starting sim at address 0x1013c4
Running...
Could not find instruction at address 0x1013d4! Ending sim...
      Address    Instruction  Hits  Misses Hit Rate
       1013c4       li s0,16     0       1    0.00%
       1013c8  addi s0,s0,-1    15       1   93.75%
       1013cc  jal ra,101368    16       0  100.00%
       1013d0 bnez s0,1013c8    15       1   93.75%
       101368            nop    15       1   93.75%
       10136c            ret    16       0  100.00%
Total                           77       4   95.06%
Instructions run: 81
```
