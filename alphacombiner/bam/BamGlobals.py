"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""

READ_UINT32 = False
WRITE_UINT32 = False

### BAM GLOBALS
BOC_push = 0
BOC_pop = 1
BOC_adjunct = 2
BOC_remove = 3
BOC_file_data = 4
### BAM GLOBALS

def read_pointer(di):
    global READ_UINT32

    if READ_UINT32:
        return di.get_uint32()

    pointer = di.get_uint16()

    if pointer == 65535:
        READ_UINT32 = True

    return pointer

def write_pointer(dg, pointer):
    global WRITE_UINT32

    if WRITE_UINT32:
        dg.add_uint32(pointer)
        return

    dg.add_uint16(pointer)

    if pointer == 65535:
        WRITE_UINT32 = True
