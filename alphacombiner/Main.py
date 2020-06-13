from .CombinerBamFile import CombinerBamFile
from .ImageConverter import ImageConverter
import argparse, glob, os

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""

def print_enabled(flag, description):
    if flag:
        print(description + '...')
    else:
        print('NOT ' + description[0].lower() + description[1:] + '.')

def main():
    parser = argparse.ArgumentParser(description='This script can be used to convert Panda3D bam models using JPG+RGB textures to use PNG textures.')
    parser.add_argument('--jpg', '-j', action='store_true', help='Convert regular JPG textures to PNG textures.')
    parser.add_argument('--rgb', '-r', action='store_true', help='Convert JPG+RGB texture combos to PNG textures.')
    parser.add_argument('--overwrite', '-o', action='store_true', help='Overwrite models instead of appending _png to the filename.')
    parser.add_argument('--convert-images', '-c', action='store_true', help='Convert all modified images to PNG in-place.')
    parser.add_argument('--wipe-jpg', '-w', action='store_true', help='Remove all JPG+RGB files that have been converted to PNG.')
    parser.add_argument('--early-exit', '-e', action='store_true', help='Exit immediately if an image could not be converted properly.')
    parser.add_argument('--phase-files', '-p', help='The location of your phase files. Required for --convert-images.')
    parser.add_argument('filenames', nargs='+', help='The raw input file(s). Accepts * as wildcard.')
    args = parser.parse_args()

    if (args.convert_images or args.wipe_jpg):
        if not args.phase_files:
            parser.print_help()
            print('You must specify your phase files folder!')
            return
        if not os.path.exists(args.phase_files):
            parser.print_help()
            print('This phase files folder does not exist!')
            return

    print_enabled(args.jpg, 'Converting regular JPG textures to PNG textures')
    print_enabled(args.rgb, 'Converting JPG + RGB texture combos to PNG textures')
    print_enabled(args.overwrite, 'Overwriting files in place')
    print_enabled(args.convert_images, 'Converting images to PNG in place')
    print_enabled(args.convert_images and args.wipe_jpg, 'Wiping old JPG images')

    converter = ImageConverter(args.early_exit)

    if args.convert_images:
        converter.set_model_path(args.phase_files)

    to_wipe = []

    for filename in args.filenames:
        files = []

        if '*' in filename:
            files = glob.glob(filename)
        else:
            files.append(filename)

        for file in files:
            bam = CombinerBamFile()

            with open(file, 'rb') as f:
                print('Loading', file + '...')
                bam.load(f)

            if args.overwrite:
                target_filename = file
            else:
                basename, ext = os.path.splitext(file)
                target_filename = os.path.join(os.path.dirname(file), basename + '_png' + ext)

            textures = bam.switch_texture_mode(args.jpg, args.rgb)

            if args.convert_images:
                converter.convert_textures(textures)

                if args.wipe_jpg:
                    for texture in textures:
                        if texture not in to_wipe:
                            to_wipe.append(texture)

            with open(target_filename, 'wb') as f:
                print('Writing', target_filename + '...')
                bam.write(f, bam.version)

    if args.wipe_jpg:
        converter.wipe_textures(args.phase_files, to_wipe)

    print('Done.')

if __name__ == '__main__':
    main()