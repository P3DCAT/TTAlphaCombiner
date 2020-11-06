from p3bamboo.BamFile import BamFile
from p3bamboo.BamFactory import BamFactory

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class CombinerBamFile(BamFile):

    def switch_texture_mode(self, convert_jpg, convert_rgb, convert_relative, base_folder):
        target_ids = self.find_related('Texture')

        if not target_ids:
            # This model has no textures.
            return [], False

        modified_textures = []
        modified = False

        for obj in self.objects:
            if obj['handle_id'] not in target_ids:
                continue

            node = BamFactory.create(self, self.version, obj['handle_name'], 'Texture')
            node.load_object(obj)

            if convert_relative and node.transform_relative(base_folder):
                modified = True

            texture = node.transform_to_png(convert_jpg, convert_rgb)

            if texture and texture not in modified_textures:
                modified_textures.append(texture)
                modified = True

            node.write_object(write_version=self.version, obj=obj)

        return modified_textures, modified
