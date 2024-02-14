
from db.db_connections import get_db_session
from db.db_models import ImageDB
from sqlalchemy import func
from s3.s3_access import download_image_from_s3

def get_random_images(numb_images=100):
    session = get_db_session()
    random_images = session.query(ImageDB).order_by(func.rand()).limit(numb_images).all()
    # for image in random_images:
    #     download_image_from_s3(image.file_name)
    return random_images

def download_images(images):
    for image in images:
        download_image_from_s3(image.file_name)

# for image in images:
#     image_name = url.split('/')[-1]  # Extract image name from the URL
#     s3.download_file('<your_bucket_name>', image_name, f'<local_directory_path>/{image_name}')

if __name__ == "__main__":

    a = get_random_images()
    print(len(a))

    # session = get_db_session()
    # random_images = session.query(ImageDB).order_by(func.rand()).limit(10).all()
    # print(len(random_images))
    # download_images(random_images)