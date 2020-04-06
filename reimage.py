import argparse


class Config:
    # TODO add Doc string
    pass


def reimage(config: Config):
    # TODO add Doc string

    import glob
    from PIL import Image

    widthOfNewImage = 400

    counterUsedAsNewNameOfImages=0
    pathOfImagesContainingFolder='C:\\Users\Talha\Desktop\Pics With Qasim\*.jpg'
    newImagesContainingFolder=r'C:\\Users\Talha\Desktop\newFolder\ '
    images = glob.glob(pathOfImagesContainingFolder)

    for image in images:

        with open(image, 'rb') as file:

            img = Image.open(file)

            wpercent = (widthOfNewImage / float(img.size[0]))
            heightOfNewImage = int((float(img.size[1]) * float(wpercent)))
            print(heightOfNewImage)
            img = img.resize((widthOfNewImage, heightOfNewImage), Image.ANTIALIAS)

            img.save(newImagesContainingFolder+ str(counterUsedAsNewNameOfImages) + '.jpg' , 'JPEG', quality=100) #Path Of The folder where the resulting images will be stored
            counterUsedAsNewNameOfImages+=1


def __init_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Converts images from the source directory to a given resolution'
                                                 'and copies the new files in destination directory.')
    parser.add_argument('source_directory',
                        type=str,
                        help='Directory whose images need to be converted.')

    parser.add_argument('destination_directory',
                        type=str,
                        help='Directory where converted files will be copied.')

    parser.add_argument('height',
                        type=int,
                        help='Height of the converted image in pixels.')

    parser.add_argument('width',
                        type=int,
                        help='Width of the converted image in pixels.')

    parser.add_argument('-t', '--target-discovery',
                        type=str,
                        choices=['shallow', 'deep'],
                        default='shallow',
                        help='How to find target files. "shallow" only includes files of the source_directory.'
                             '"deep" includes all files in the source_directory, including subdirectory files.')

    parser.add_argument('-s', '--save-structure',
                        type=str,
                        choices=['root', 'source'],
                        default='root',
                        help='Where to save converted files. "root" saves all files in destination_directory'
                             '"source" saves files in a directory structure similar to source_directory.'
                             'Note: In "root", filenames have numbers appended to avoid conflicts.')
    parser.add_argument('-b', '--background-type',
                        type=str,
                        choices=['solid-black', 'noise'],
                        default='noise',
                        help='Background type to use when converted image does not cover the entire space given in'
                        '"height" and "width".')

    parser.add_argument('-p', '--padding',
                        type=str,
                        choices=['start', 'center', 'end'],
                        default='center',
                        help='Sides to pad to make the resized image equal to given size.'
                        'It could be thought as the alignment of resized image in a container of given size.')

    return parser


if __name__ == '__main__':
    import sys

    args_parser = __init_arg_parser()
    args = args_parser.parse_args()

    config = Config()  # TODO make config from args
    print("DOne")
    # reimage(config=config)


# Scrap Code Snippets
import os
for path, directories, files in os.walk("."):
    break