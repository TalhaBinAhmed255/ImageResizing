# ReImage

A bulk image resizing utility. Takes images from a source directory and saves converted images in a destination directory.

# Dependencies

* [numpy](https://pypi.org/project/numpy/)
* [Pillow](https://pypi.org/project/Pillow/2.1.0/)

```bash
$ pip install numpy pillow
```

# Usage

> Use python >= 3.6

```
usage: reimage.py [-h] [-t {shallow,deep}] [-s {root,source}]
                  [-b {solid-black,noise}] [-p {start,center,end}]
                  source_directory destination_directory width height

Converts images from the source directory to a given resolutionand copies the
new files in destination directory.

positional arguments:
  source_directory      Directory whose images need to be converted.
  destination_directory
                        Directory where converted files will be copied.
  width                 Width of the converted image in pixels.
  height                Height of the converted image in pixels.

optional arguments:
  -h, --help            show this help message and exit
  -t {shallow,deep}, --target-discovery {shallow,deep}
                        How to find target files. "shallow" only includes
                        files of the source_directory."deep" includes all
                        files in the source_directory, including subdirectory
                        files.
  -s {root,source}, --save-structure {root,source}
                        Where to save converted files. "root" saves all files
                        in destination_directory"source" saves files in a
                        directory structure similar to source_directory.Note:
                        In "root", filenames have numbers appended to avoid
                        conflicts.
  -b {solid-black,noise}, --background-type {solid-black,noise}
                        Background type to use when converted image does not
                        cover the entire space given in"height" and "width".
  -p {start,center,end}, --padding-alignment {start,center,end}
                        Sides to pad to make the resized image equal to given
                        size.It could be thought as the alignment of resized
                        image in a container of given size.
                        
```
# Example
Resize images in [./Demo/original](./Demo/original) using the command:
```bash
$ python reimage.py ./Demo/original ./Demo/resized 400 400 -t deep -s source -b noise -p end
```

# Customize

To define a new background type simply implement a `BackgroundInterface` and update `BackgroundFactory` and add a value in `--background-type` for it. 
