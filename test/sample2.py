import sys
sys.path.append('..')
from ibex_icache.icache import CacheConfiguration, IbexICache
from ibex_icache.sim import ICacheSim

# Default configuration
cache_config = CacheConfiguration(
    size = 8192, 
    ways = 2, 
    line_size = 16)

cache = IbexICache(32, cache_config)
sim = ICacheSim()
sim.load_instr("asm/sample2.lst")
sim.sim(cache, 1000)
sim.print_result()
