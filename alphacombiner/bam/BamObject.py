from panda3d.core import Datagram, DatagramIterator

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class BamObject(object):

    def __init__(self, bam_version):
        self.bam_version = bam_version
        self.extra_data = b''

    def load_object(self, obj):
        dg = Datagram(obj['data'])
        di = DatagramIterator(dg)
        self.load(di)

    def write_object(self, write_version, obj):
        dg = Datagram()
        self.write(write_version, dg)
        obj['data'] = dg.get_message()

    def load(self, di):
        pass

    def write(self, write_version, dg):
        pass
