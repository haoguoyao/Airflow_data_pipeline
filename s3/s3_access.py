
import s3.s3_settings as s3_settings
from s3.s3_connection import s3_client
from botocore.exceptions import NoCredentialsError
from s3.s3_settings import bucket_name, S3_FOLDER, S3_withbox_FOLDER, S3_cropped_FOLDER

def upload_to_s3(file_name, bucket_name, object_name):
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
    except NoCredentialsError:
        print("Credentials not available")
        return False
    return True



def delete_s3_folder(folder_name):

    if not folder_name.endswith('/'):
        folder_name += '/'
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    # Delete the objects
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"Deleting {obj['Key']}")
            s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
            print(f"Deleted {obj['Key']}")

        print(f"Deleted all objects in folder '{folder_name}' from bucket '{bucket_name}'.")
    else:
        print(f"No objects found in folder '{folder_name}'.")
    return 


def download_image_from_s3(file_name, local_path):
    """
    Download an image from S3 to a local directory.

    :param file_name: Name of the file in S3.
    :param local_path: Local directory to save the downloaded file. Defaults to 'downloaded_images/'.
    """
    try:
        # Ensure local_path exists
        import os
        os.makedirs(local_path, exist_ok=True)
        
        # Full path where the image will be saved
        local_file_path = os.path.join(local_path, file_name)
        # print(local_file_path)
        
        # Full S3 key (path) of the image
        s3_key = f"{S3_FOLDER}{file_name}" if S3_FOLDER else file_name

        # Download the file
        s3_client.download_file(bucket_name, s3_key, local_file_path)
        print(f"Downloaded {file_name} to {local_file_path}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")



def empty_s3_predictions():
    delete_s3_folder(S3_withbox_FOLDER)
    delete_s3_folder(S3_cropped_FOLDER)
    return

if __name__=="__main__":

    # upload_to_s3('category_counts.png',bucket_name,'coco_yolov4_result/sample_output_image2.jpg')
    empty_s3_predictions()