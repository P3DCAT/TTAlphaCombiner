from panda3d.core import Filename, PNMImage
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

    def read_texture(self, filename, alpha=False):
        """
        Reads a texture from the model path.
        Throws a PalettizerException if file could not be found.
            :filename: Relative filename pointing to a texture file in the model path.
            :alpha: Do we need an alpha channel?
        """
        img = PNMImage()
        img.read(Filename.from_os_specific(filename))

        if alpha:
            needs_alpha_fill = img.num_channels not in (2, 4)
            img.set_color_type(4)

            if needs_alpha_fill:
                # We need an alpha channel no matter what, so if the image does not have one,
                # it needs to be filled immediately with opaque pixels as it starts out with transparent pixels
                img.alpha_fill(1)
        else:
            img.set_color_type(3)

        return img

    def resize_image(self, image, x_size, y_size):
        """
        Resize an image using the Gaussian blur algorithm.
            :image: A PNMImage representing your image data.
            :x_size: The desired X size of the texture.
            :y_size: The desired Y size of the texture.
        """
        if image.get_x_size() == x_size and image.get_y_size() == y_size:
            # This image does not need to be resized!
            return image

        print(f'Implicit resize from ({image.get_x_size()}, {image.get_y_size()}) to {x_size, y_size}')

        # Resize the image using Panda3D's gaussian filter algorithm, to fit our x_size and y_size.
        # WARNING! This blurs the image if too small!!! (Gaussian blur)
        new_image = PNMImage(x_size, y_size, image.get_num_channels(), image.get_maxval(), image.get_type())
        new_image.gaussian_filter_from(1.0, image)

        return new_image

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

        if len(texture) == 1:
            # Only one texture, we can save this immediately
            output_img = self.read_texture(tex_path, alpha=False)
        elif len(texture) == 2:
            img = self.read_texture(tex_path, alpha=True)

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

            alpha_img = PNMImage()
            alpha_img.read(Filename.from_os_specific(alpha_path))

            alpha_img = self.resize_image(alpha_img, img.get_x_size(), img.get_y_size())

            output_img = PNMImage(img.get_x_size(), img.get_y_size(), 4)
            output_img.alpha_fill(1)

            output_img.copy_sub_image(img, 0, 0, 0, 0, img.get_x_size(), img.get_y_size())

            for i in range(img.get_x_size()):
                for j in range(img.get_y_size()):
                    output_img.set_alpha(i, j, alpha_img.get_gray(i, j))

        output_img.write(Filename.from_os_specific(png_tex_path))

    def convert_all(self):
        for root, _, files in os.walk(self.model_path):
            for file in files:
                full_path = os.path.relpath(os.path.join(root, file), self.model_path)

                if not full_path.lower().endswith('.jpg'):
                    continue

                filename_wo_ext = os.path.splitext(full_path)[0]
                rgb = filename_wo_ext + '_a.rgb'

                if not os.path.exists(os.path.join(self.model_path, rgb)):
                    rgb = filename_wo_ext + '.rgb'

                    if not os.path.exists(os.path.join(self.model_path, rgb)):
                        rgb = None

                if rgb:
                    input_files = [full_path, rgb]
                else:
                    input_files = [full_path]

                self.convert_texture(input_files)

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
