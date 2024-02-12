
import s3.s3_settings as s3_settings
from s3.s3_connection import s3_client
from botocore.exceptions import NoCredentialsError

def upload_to_s3(file_name, bucket_name, object_name):
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
    except NoCredentialsError:
        print("Credentials not available")
        return False
    return True

def download_from_s3(bucket_name, object_name, file_name):
    try:
        s3_client.download_file(bucket_name, object_name, file_name)
    except NoCredentialsError:
        print("Credentials not available")
        return False
    return True


def download_image_from_s3(file_name, local_path='downloaded_images/'):
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
        
        # Full S3 key (path) of the image
        s3_key = f"{S3_FOLDER}{file_name}" if S3_FOLDER else file_name
        
        # Download the file
        s3_client.download_file(S3_BUCKET, s3_key, local_file_path)
        print(f"Downloaded {file_name} to {local_file_path}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")