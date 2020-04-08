import argparse
import os
import re
import time
from abc import ABC, abstractmethod

import numpy as np
from PIL import Image


DEBUG = r'.\Demo\debug'

IMAGE_FILE_EXTENSION_REGEX = re.compile(r"^.+\.((?:jpg)|(?:jpeg)|(?:png))$")


class BackgroundInterface(ABC):
    """
    Interface for Background image generating classes.
    """
    @abstractmethod
    def __init__(self, size: (int, int)):
        pass

    @abstractmethod
    def get_image(self, mode: str) -> Image:
        """
        Returns a background PIL.Image according to the size passed to the class during initialization.
        :param mode: PIL.Image's mode
        :return: An image.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """
        Returns a string used to identify this Background class.
        :return: name of the background class.
        """
        pass


class SolidBlackBackground(BackgroundInterface):
    @staticmethod
    def get_name() -> str:
        return 'solid-black'

    def __init__(self, size: (int, int)):
        super().__init__(size)

        color = '#000'

        # cache images for faster generation of backgrounds
        self.__cache = {
            '1': Image.new('1', size, color),
            'L': Image.new('L', size, color),
            'P': Image.new('P', size, color),
            'RGB': Image.new('RGB', size, color),
            'RGBA': Image.new('RGBA', size, color),
            'CMYK': Image.new('CMYK', size, color),
            'YCbCr': Image.new('YCbCr', size, color),
            'LAB': Image.new('LAB', size, color),
            'HSV': Image.new('HSV', size, color),
            'I': Image.new('I', size, color),
            'F': Image.new('F', size, color)
        }

    def get_image(self, mode: str) -> Image:
        return self.__cache[mode].copy()


class RandomNoiseBackground(BackgroundInterface):
    @staticmethod
    def get_name() -> str:
        return 'noise'

    def __init__(self, size: (int, int)):
        super().__init__(size)

        self.size = size
        self.limits = np.iinfo('int32')

    def get_image(self, mode: str) -> Image:
        random_values = np.random.randint(self.limits.min, high=self.limits.max, size=self.size)
        return Image.fromarray(random_values, mode)


class BackgroundFactory:
    """
    Creates Background generator classes.
    """
    @staticmethod
    def get_background(name: str, size: (int, int)) -> BackgroundInterface:
        """
        Returns an instance of a Background generating class according to the param name.
        :param name: A string corresponding.
        :param size: Size of the image to be returns as (width, height).
        :return:
        """
        if name == SolidBlackBackground.get_name():
            return SolidBlackBackground(size)
        elif name == RandomNoiseBackground.get_name():
            return RandomNoiseBackground(size)


class ReImage:
    """
    Changes the dimensions of files in a source directory to given values and stores them in a destination directory.
    """
    def __init__(self, args_namespace: argparse.Namespace):
        """
        :param args_namespace: contains args to specify several properties that determine behavior.
                               Refer to GitHub repo.
        """
        # Extract args
        self.width = args_namespace.width
        self.height = args_namespace.height
        self.source_directory = args_namespace.source_directory
        self.destination_directory = args_namespace.destination_directory
        self.target_discovery = args_namespace.target_discovery
        self.save_structure = args_namespace.save_structure
        self.background_type = args_namespace.background_type
        self.padding_alignment = args_namespace.padding_alignment

        # Initialize
        self.current_directory = self.source_directory
        self.background = BackgroundFactory.get_background(self.background_type, (self.width, self.height))
        self.image_counter = 0

    def run(self):
        """Starts the conversion process."""

        if self.target_discovery == 'shallow':
            self.current_directory, _, files = os.walk(self.source_directory).__next__()
            self.__process_files(files)

        elif self.target_discovery == 'deep':
            for self.current_directory, _, files in os.walk(self.source_directory):
                self.__process_files(files)

        print(f'\n\tTotal files converted: {self.image_counter}\n')

    def __process_files(self, files: [str]):
        """
        Converts all files in the files list.
        :param files: A list of file names.
        :return: Nothing.
        """
        for filename in files:
            filepath = os.path.join(self.current_directory, filename)
            if IMAGE_FILE_EXTENSION_REGEX.match(filename):
                image = self.__convert_image(filepath)
                self.__save_image(image, filename)

    def __convert_image(self, image_filepath: str) -> Image:
        """
        Converts a single image to new size.
        :param image_filepath: Complete path of the file.
        :return: Converted Image.
        """
        image = Image.open(image_filepath)

        # For some reason, paste function did not work on these modes when a PNG of bit depth of 1, 8, or 16 was used.
        # I convert them to RGBA, which works fine.
        if image.mode in ('1', 'L', 'P'):
            image = image.convert('RGBA')

        size, padding = self.__calculate_new_image_size(
            old_img_size=image.size, new_img_size=(self.width, self.height))

        image = image.resize(size, Image.ANTIALIAS)

        return self.__apply_to_background(image, padding)

    @staticmethod
    def __calculate_new_image_size(old_img_size: (int, int), new_img_size: (int, int)) -> ((int, int), (int, int)):
        """
        Calculates what size an image with old_img_size would have to become if we want to place it in an image
        of new_img_size, along with the padding required on vertical and horizontal axis.
        :param old_img_size: (width, height) of an image which needs resizing.
        :param new_img_size: (width, height) of an image in which the other image is to be pasted.
        :return: (new_width, new_height), (new_horizontal_padding, new_vertical_padding)
        """
        ratio_old = ReImage.__calculate_size_ratio(old_img_size)
        ratio_new = ReImage.__calculate_size_ratio(new_img_size)

        if ratio_old > ratio_new:
            new_width = new_img_size[0]
            scale_factor = new_width / old_img_size[0]
            new_height = int(old_img_size[1] * scale_factor)
        else:
            new_height = new_img_size[1]
            scale_factor = new_height / old_img_size[1]
            new_width = int(old_img_size[0] * scale_factor)

        new_horizontal_padding = abs(new_width - new_img_size[0])
        new_vertical_padding = abs(new_height - new_img_size[1])

        return (new_width, new_height), (new_horizontal_padding, new_vertical_padding)

    @staticmethod
    def __calculate_size_ratio(img_size: (int, int)) -> float:
        return img_size[0] / img_size[1]

    def __apply_to_background(self, image: Image, padding: (int, int)) -> Image:
        """
        Pastes image on a background.
        :param image: Image to be pasted onto a background.
        :param padding: The free space that will be left behind after the pasting.
        :return: image of proper size with a background.
        """
        if self.padding_alignment == 'start':
            box = (0, 0)
        elif self.padding_alignment == 'end':
            box = padding
        else:
            box = (int(padding[0]/2), int(padding[1]/2))

        bg_image = self.background.get_image(image.mode)

        bg_image.paste(image, box=box)

        return bg_image

    def __save_image(self, image: Image, filename: str):
        """
        Stores the image on the system.
        :param image: image to store.
        :param filename: the filename of the image.
        :return: nothing.
        """
        destination_directory_temp = self.destination_directory
        new_filename = f'{ReImage.__current_milli_time()}{self.image_counter} {filename}'

        if self.save_structure == 'source':
            partial_path = self.current_directory[len(self.source_directory):]
            if partial_path and partial_path[0] == os.path.sep:
                partial_path = partial_path[1:]
            destination_directory_temp = os.path.join(self.destination_directory, partial_path)
            destination_filepath = os.path.join(destination_directory_temp, new_filename)
        else:
            destination_filepath = os.path.join(self.destination_directory, new_filename)

        os.makedirs(destination_directory_temp, exist_ok=True)
        image.save(destination_filepath, quality=100)

        print(f'SAVED: {destination_filepath}')

        self.image_counter += 1

    @staticmethod
    def __current_milli_time() -> int:
        return int(round(time.time() * 1000))


def __init_arg_parser() -> argparse.ArgumentParser:
    """
    Configures an ArgumentParser with the arguments needed for this script.

    :return: Configured ArgumentParser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Converts images from the source directory to a given resolution'
                                                 'and copies the new files in destination directory.')
    parser.add_argument('source_directory',
                        type=str,
                        help='Directory whose images need to be converted.')

    parser.add_argument('destination_directory',
                        type=str,
                        help='Directory where converted files will be copied.')

    parser.add_argument('width',
                        type=int,
                        help='Width of the converted image in pixels.')

    parser.add_argument('height',
                        type=int,
                        help='Height of the converted image in pixels.')

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
                        default='solid-black',
                        help='Background type to use when converted image does not cover the entire space given in'
                        '"height" and "width".')

    parser.add_argument('-p', '--padding-alignment',
                        type=str,
                        choices=['start', 'center', 'end'],
                        default='center',
                        help='Sides to pad to make the resized image equal to given size.'
                        'It could be thought as the alignment of resized image in a container of given size.')

    return parser


if __name__ == '__main__':
    args_parser = __init_arg_parser()
    args = args_parser.parse_args()

    assert os.path.isdir(args.source_directory), f'Source Directory "{args.source_directory}" does not exist.'

    if not os.path.isdir(args.destination_directory):
        os.makedirs(args.destination_directory)
    if not os.listdir(args.destination_directory):
        ReImage(args).run()
    else:
        print('\nDestination directory not empty. Cannot continue.\n')

