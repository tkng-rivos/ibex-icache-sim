import sys
sys.path.append('..')
from ibex_icache.icache import CacheConfiguration, IbexICache
from ibex_icache.sim import ICacheSim

# Default configuration
cache_config = CacheConfiguration(
    size = 4096, 
    ways = 2, 
    line_size = 8)

cache = IbexICache(32, cache_config)
sim = ICacheSim()
sim.load_instr("asm/sample.lst")
sim.sim(cache, 100)
sim.print_result()

