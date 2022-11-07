import math

DEFAULT_CACHE_SIZE = 4096
DFEAULT_WAYS = 2
DEFAULT_LINE_SIZE = 8

class IbexICache:
    """Ibex ICache"""
    def __init__(self, addr_width, cache_config):
        self.addr_width = addr_width
        self.params = cache_config
        self.line_bits = int(math.log2(self.params.line_size))
        self.blocks = int(self.params.size / (self.params.ways * self.params.line_size))
        self.idx_bits = int(math.log2(self.blocks))
        self.tag_bits = addr_width - self.line_bits - self.idx_bits
        # Init tag entries
        self.tag_entries = [[(False, 0) for j in range(self.params.ways)] for i in range(self.blocks)]
        self.evict_rr = 1

    def tag_from_addr(self, addr):
        # Shift & Mask
        return (addr >> (self.line_bits + self.idx_bits)) & ((1 << self.tag_bits) - 1)

    def idx_from_addr(self, addr):
        # Shift & Mask
        return (addr >> self.line_bits) & ((1 << self.idx_bits) - 1)

    def is_hit(self, addr):
        """Cache hit or miss?"""
        # Round robin needs to be updated every cycle... pseduo random.
        self.evict_rr = (self.evict_rr + 1) % self.params.ways
        # Check Cache
        entry = self.tag_entries[self.idx_from_addr(addr)]
        self.lowest_inval = self.params.ways
        way = 0
        hit = False
        # In reality these comparisons are done in parallel
        for (valid, tag) in entry:
            if valid and tag == self.tag_from_addr(addr):
                # If way matches
                hit = True
            elif way < self.lowest_inval:
                # Else assign lowest inval way, if not already done so
                self.lowest_inval = way
            way += 1
        return hit
    
    def evict_and_alloc(self, addr):
        """Default eviction strategy and allocate new entry"""
        tag = self.tag_from_addr(addr)
        idx = self.idx_from_addr(addr)
        entry = self.tag_entries[idx]
        if self.lowest_inval < self.params.ways:
            # Use lowest invalid way
            entry[self.lowest_inval] = (True, tag)
        else:
            entry[self.evict_rr] = (True, tag)

class CacheConfiguration:
    """Cache configuration"""
    def __init__(self, size, ways, line_size):
        self.size = size   # Cache size (bytes)
        self.ways = ways      # Cache ways
        self.line_size = line_size # Cache line size (bytes)
        
    def __str__(self):
        return 'Cache:\n -Size: {0}\n -Ways: {1}\n -Line Size: {2}'.format(self.size, self.ways, self.line_size)


