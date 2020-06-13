# TT Alpha Combiner

TT Alpha Combiner is used to convert Panda3D BAM models to use PNG textures instead of JPG + RGB textures.

This tool is capable of rewriting BAM files while preserving all node data.

It can either rewrite all BAM files in-place or create new copies of each BAM file.
By default, `_png` is appended to the end of each BAM filename.

* Use the `--jpg` flag to rewrite BAM files using regular JPG textures without RGB files.
* Use the `--rgb` flag to rewrite BAM files using JPG+RGB combo textures.
* Use the `--overwrite` flag to overwrite all BAM files in-place.
* Using the `--convert-images` flag, Alpha Combiner will convert all JPG and RGB files associated with your models to PNG automatically.
* Use the `--wipe-jpg` flag if you want all converted JPG files to be deleted after conversion. Requires the `--convert-images` flag.
* Use the `--early-exit` flag to halt execution of the program if any textures are missing.
* The `--convert-images` flag requires you to set the phase files location using `--phase-files`. Example: `--phase-files C:/Data/Toontown/resources`, `resources` being the folder that stores `phase_3`, `phase_4`, etc.

Wildcards can be used to specify the models to rewrite, but are not required.

## Installation

Your Python version must be at least 3.6, but newer versions are appreciated.

Make sure you've got Panda3D installed. The newer, the better.

You must clone the repository. This project has one dependency: `Pillow`, which can be installed using pip.

```
git clone https://github.com/darktohka/TTAlphaCombiner
cd TTAlphaCombiner
python -m pip install -r requirements.txt
```

## Running

```
usage: python -m alphacombiner.Main [-h] [--jpg] [--rgb] [--overwrite] [--convert-images] [--wipe-jpg] [--early-exit] [--phase-files PHASE_FILES] filenames [filenames ...]

This script can be used to convert Panda3D bam models using JPG+RGB textures to use PNG textures.

positional arguments:
  filenames             The raw input file(s). Accepts * as wildcard.

optional arguments:
  -h, --help            show this help message and exit
  --jpg, -j             Convert regular JPG textures to PNG textures.
  --rgb, -r             Convert JPG+RGB texture combos to PNG textures.
  --overwrite, -o       Overwrite models instead of appending _png to the filename.
  --convert-images, -c  Convert all modified images to PNG in-place.
  --wipe-jpg, -w        Remove all JPG+RGB files that have been converted to PNG.
  --early-exit, -e      Exit immediately if an image could not be converted properly.
  --phase-files PHASE_FILES, -p PHASE_FILES
                        The location of your phase files. Required for --convert-images.
```

For example, to rewrite all models using JPG+RGB textures in `phase_6/modules`, while keeping the original copies of the models, and also converting all JPG+RGB textures to PNG:

```
python -m alphacombiner.Main --jpg --rgb --convert-images --phase-files C:/Data/Toontown/resources C:/Data/Toontown/resources/phase_6/modules/*.bam
```

## Caveats

You might already have some PNG files that are different than the JPG+RGB combo textures. Such an example might be `toontown-logo.jpg` (old Toontown logo) and `toontown-logo.png` (your project's logo). The PNG file will be overwritten when using `--convert-images`. Beware.

Some alpha RGB channels are larger than the source JPG file. Alpha Combiner will complain. Those files have to be fixed manually. (Only when using `--convert-images`)

Some RGB files used by fonts have both grayscale and transparency channels. Pillow can't open these and these have to be converted manually. (Only when using `--convert-images`)

Errors might occur when using `--convert-images`. To quit the program as soon as an error is encountered, use the `--early-exit` flag. Otherwise, look for lines marked as `ERROR:` in the output after running the program to fix these textures manually.

## Known Bugs

Some RGB files, mostly those used for fonts, are grayscale but with transparency enabled. For example: `phase_3/maps/phase_3_palette_2tmlc_1.rgb` used by `phase_3/models/fonts/MickeyFont.bam`

Those RGB files cannot be read by Pillow, and, as such, cannot be converted to PNG textures by the `--convert-images` flag. For now, convert those special grayscale transparent RGB images manually using GIMP.
