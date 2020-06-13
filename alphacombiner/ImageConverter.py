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
        self.converted_so_far = []

    def print_exc(self, *args):
        if self.early_exit:
            raise Exception(' '.join(args))

        print(*args)

    def convert_texture(self, texture, model_path=None):
        if not self.model_path:
            self.print_exc('ERROR: No model path specified in ImageConverter.')
            return

        tex_path = texture[0]
        tex_basename = os.path.splitext(os.path.basename(tex_path))[0]

        if '../' in tex_path and model_path:
            # This texture path is using relative paths.
            # We assume that the working directory is the model's directory
            tex_path = os.path.join(os.path.dirname(model_path), tex_path)
        else:
            tex_path = os.path.join(self.model_path, tex_path)

        tex_path = tex_path.replace('\\', os.sep).replace('/', os.sep)

        if not os.path.exists(tex_path):
            self.print_exc('ERROR: Could not convert {}: Missing RGB texture!'.format(tex_path))
            return

        png_tex_path = os.path.join(os.path.dirname(tex_path), tex_basename + '.png')
        png_tex_path = png_tex_path.replace('\\', os.sep).replace('/', os.sep)

        print('Converting to PNG...', png_tex_path)

        try:
            img = Image.open(tex_path)
        except Exception as e:
            self.print_exc('ERROR: Could not convert {}: Could not open using Pillow!'.format(tex_path))
            return

        if len(texture) == 1:
            # Only one texture, we can save this immediately
            output_img = img
        elif len(texture) == 2:
            # Two textures: the second one should be a RGB file
            alpha_path = texture[1]

            if '../' in alpha_path and model_path:
                # This texture path is using relative paths.
                # We assume that the working directory is the model's directory
                alpha_path = os.path.join(os.path.dirname(model_path), alpha_path)
            else:
                alpha_path = os.path.join(self.model_path, alpha_path)

            alpha_path = alpha_path.replace('\\', os.sep).replace('/', os.sep)

            if not os.path.exists(alpha_path):
                self.print_exc('ERROR: Could not convert {} with alpha {}: Missing alpha texture!'.format(tex_path, alpha_path))
                return

            try:
                alpha_img = Image.open(alpha_path)
            except Exception as e:
                self.print_exc('ERROR: Could not convert {} with alpha {}: Could not open alpha file using Pillow!'.format(tex_path, alpha_path))
                return

            if alpha_img.size != img.size:
                self.print_exc('ERROR: Could not convert {} with alpha {}: Image size and alpha size does NOT match! Image: {} Alpha: {}'.format(tex_path, alpha_path, img.size, alpha_img.size))
                return

            output_img = Image.new('RGBA', img.size, (255, 255, 255))

            rgb_pixels = img.load()
            alpha_pixels = alpha_img.load()
            output_pixels = output_img.load()

            width, height = output_img.size

            # Merge RGB and Alpha data
            if img.getbands() == ('L',):
                # Grayscale image
                for i in range(width):
                    for j in range(height):
                        l = rgb_pixels[i,j]
                        a = alpha_pixels[i,j]

                        # For alpha RGBs that have more than one channel
                        if type(a) != int: a = a[0]

                        output_pixels[i,j] = (l, l, l, a)
            else:
                # RGB image
                for i in range(width):
                    for j in range(height):
                        r, g, b = rgb_pixels[i,j]
                        a = alpha_pixels[i,j]

                        # For alpha RGBs that have more than one channel
                        if type(a) != int: a = a[0]

                        output_pixels[i,j] = (r, g, b, a)

        output_img.save(png_tex_path)

    def convert_textures(self, textures, model_path=None):
        for texture in textures:
            if texture in self.converted_so_far:
                # We've already converted this texture...!!!
                # Don't do the same work twice.
                continue

            self.convert_texture(texture, model_path)
            self.converted_so_far.append(texture)

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
