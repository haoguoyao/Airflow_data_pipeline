
from db.db_operations import get_random_images
from s3.s3_access import download_image_from_s3
import os



def download_images(images,path):
    for image in images:
        download_image_from_s3(image.file_name,path)
    return

def get_images_local_folder(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        # Construct absolute file path
        file_path = os.path.join(folder_path, filename)
        # Check if the current file is a file (not a directory)
        if os.path.isfile(file_path):
            images.append(file_path)
    return images


if __name__ == "__main__":

    images = get_random_images(100)
    print(len(images))
    download_images(images,'ml_model/downloaded_images2/')

    # session = get_db_session()
    # random_images = session.query(ImageDB).order_by(func.rand()).limit(10).all()
    # print(len(random_images))
    # download_images(random_images)