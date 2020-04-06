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


if __name__ == '__main__':

    # TODO configure and parse args

    config = Config()  # TODO make config from args
    reimage(config=config)


# Scrap Code Snippets
import os
for path, directories, files in os.walk("."):
    break