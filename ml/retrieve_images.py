
from db.db_connections import get_db_session
from db.db_models import ImageDB
from sqlalchemy import func
import coco.coco_models as coco_models
from s3.s3_access import download_image_from_s3
import os

def get_random_images(numb_images=100):
    session = get_db_session()
    random_images = session.query(ImageDB).order_by(func.rand()).limit(numb_images).all()
    # for image in random_images:
    #     download_image_from_s3(image.file_name)
    images = [coco_models.convert_image_from_sql_to_pydantic(image) for image in random_images]
    return images

def download_images(images):
    for image in images:
        download_image_from_s3(image.file_name)

def get_images_local_folder(folder_path="ml_model/downloaded_images"):
    images = []
    for filename in os.listdir(folder_path):
        # Construct absolute file path
        file_path = os.path.join(folder_path, filename)
        # Check if the current file is a file (not a directory)
        if os.path.isfile(file_path):
            images.append(file_path)
    return images


if __name__ == "__main__":

    a = get_random_images()
    print(len(a))
    download_images(a)

    # session = get_db_session()
    # random_images = session.query(ImageDB).order_by(func.rand()).limit(10).all()
    # print(len(random_images))
    # download_images(random_images)