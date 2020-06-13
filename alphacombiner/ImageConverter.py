from PIL import Image
import os

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class ImageConverter(object):

    def __init__(self, model_path, early_exit=False):
        self.model_path = model_path
        self.early_exit = early_exit

    def print_exc(self, *args):
        if self.early_exit:
            raise Exception(' '.join(args))

        print(*args)

    def convert_texture(self, texture):
        if not self.model_path:
            self.print_exc('No model path specified in ImageConverter.')
            return

        tex_path = texture[0]
        tex_basename = os.path.splitext(os.path.basename(tex_path))[0]

        tex_path = os.path.join(self.model_path, tex_path)
        tex_path = tex_path.replace('\\', os.sep).replace('/', os.sep)

        if not os.path.exists(tex_path):
            self.print_exc('Could not convert {}: Missing texture!'.format(tex_path))
            return

        png_tex_path = os.path.join(os.path.dirname(tex_path), tex_basename + '.png')
        png_tex_path = png_tex_path.replace('\\', os.sep).replace('/', os.sep)

        print('Converting to PNG...', png_tex_path)

        img = Image.open(tex_path)

        if len(texture) == 1:
            # Only one texture, we can save this immediately
            output_img = img
        elif len(texture) == 2:
            # Two textures: the second one should be a RGB file
            alpha_path = os.path.join(self.model_path, texture[1])
            alpha_path = alpha_path.replace('\\', os.sep).replace('/', os.sep)

            if not os.path.exists(alpha_path):
                self.print_exc('Could not convert {}: Missing RGB texture!'.format(alpha_path))
                return

            alpha_img = Image.open(alpha_path)
            output_img = Image.new('RGBA', img.size, (255, 255, 255))

            rgb_pixels = img.load()
            alpha_pixels = alpha_img.load()
            output_pixels = output_img.load()

            width, height = output_img.size

            # Merge RGB and Alpha data
            for i in range(width):
                for j in range(height):
                    r, g, b = rgb_pixels[i,j]
                    output_pixels[i,j] = (r, g, b, alpha_pixels[i,j])

        output_img.save(png_tex_path)

    def convert_textures(self, textures):
        for texture in textures:
            self.convert_texture(texture)

    def wipe_texture(self, folder, texture):
        jpg = os.path.join(folder, texture[0])

        if os.path.exists(jpg):
            print('Removing old JPG', jpg + '...')
            os.remove(jpg)

        if len(texture) > 1:
            rgb = os.path.join(folder, texture[1])

            if os.path.exists(rgb):
                print('Removing old RGB', rgb + '...')
                os.remove(rgb)

    def wipe_textures(self, folder, textures):
        for texture in textures:
            self.wipe_texture(folder, texture)
