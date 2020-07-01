from .Texture import Texture

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class BamFactory(object):

    def __init__(self):
        self.elements = {
            'Texture': Texture
        }

    def create(self, bam_file, handle_name, bam_version, base_name=None):
        if handle_name in self.elements:
            return self.elements[handle_name](bam_file, bam_version)
        if base_name in self.elements:
            return self.elements[base_name](bam_file, bam_version)
