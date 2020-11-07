from p3bamboo.BamFile import BamFile

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class CombinerBamFile(BamFile):

    def switch_texture_mode(self, convert_jpg, convert_rgb, convert_relative, base_folder):
        all_transformations = []
        modified = False

        for texture in self.get_objects_of_type('Texture'):
            if convert_relative and texture.transform_relative(base_folder):
                modified = True

            transformation = texture.transform_to_png(convert_jpg, convert_rgb)

            if transformation and transformation not in all_transformations:
                all_transformations.append(transformation)
                modified = True

            texture.save()

        return all_transformations, modified
