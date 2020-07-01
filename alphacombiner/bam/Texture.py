from .BamObject import BamObject
import os

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class Texture(BamObject):

    def __init__(self, bam_file, bam_version):
        BamObject.__init__(self, bam_file, bam_version)

    def load(self, di):
        self.name = di.get_string()
        self.filename = di.get_string()
        self.alpha_filename = di.get_string()

        if self.bam_version >= (4, 2):
            self.primary_file_num_channels = di.get_uint8()
        else:
            self.primary_file_num_channels = 0

        if self.bam_version >= (4, 3):
            self.alpha_file_channel = di.get_uint8()
        else:
            self.alpha_file_channel = 0

        # There used to be a proper implementation here, using
        # BAM file versions, but being highly untested, this is more secure.
        # We'll just read everything we need to change, and nothing else.
        self.texture_data = di.extract_bytes(di.get_remaining_size())

    def write(self, write_version, dg):
        dg.add_string(self.name)
        dg.add_string(self.filename)
        dg.add_string(self.alpha_filename)

        if write_version >= (4, 2):
            dg.add_uint8(self.primary_file_num_channels)

        if write_version >= (4, 3):
            dg.add_uint8(self.alpha_file_channel)

        dg.append_data(self.texture_data)

    def transform_relative(self, base_folder):
        model_dir = os.path.dirname(self.bam_file.get_filename())
        modified = False

        if self.filename and '..' in self.filename:
            filename = os.path.abspath(os.path.join(model_dir, self.filename))
            filename = os.path.relpath(filename, base_folder)
            filename = filename.replace('\\', '/')

            print('Transformed', self.filename, 'to', filename)
            self.filename = filename
            modified = True

        if self.alpha_filename and '..' in self.alpha_filename:
            alpha_filename = os.path.abspath(os.path.join(model_dir, self.alpha_filename))
            alpha_filename = os.path.relpath(alpha_filename, base_folder)
            alpha_filename = alpha_filename.replace('\\', '/')

            print('Transformed', self.alpha_filename, 'to', alpha_filename)
            self.alpha_filename = alpha_filename
            modified = True

        return modified

    def transform_to_png(self, convert_jpg=False, convert_rgb=False):
        rgb = self.alpha_filename.lower().endswith('.rgb')

        if rgb and not convert_rgb:
            return []
        if (not rgb) and not convert_jpg:
            return []

        old_filename = self.filename
        transformed = []

        # Convert primary filename to PNG
        self.filename = os.path.splitext(self.filename)[0] + '.png'

        if self.filename != old_filename:
            if self.alpha_filename:
                print('Transformed', old_filename, 'and', self.alpha_filename, 'to', self.filename)
                transformed = [old_filename, self.alpha_filename]
            else:
                print('Transformed', old_filename, 'to', self.filename)
                transformed = [old_filename]

        # Reset alpha filename (we don't need a seperate file)
        self.alpha_filename = ''

        # Toontown model files tend to limit the primary file channels to ignore alpha.
        # Now that we're using a PNG, we need to have transparency (fourth channel).
        # Let's not reset any channels.
        self.primary_file_num_channels = 0
        self.alpha_file_channel = 0

        return transformed
