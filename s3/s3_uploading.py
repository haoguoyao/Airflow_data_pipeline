import boto3
import s3.s3_settings as s3_settings
from s3_connection import s3_client
def upload_to_s3(file_path, bucket_name, object_name):
    s3_client.upload_file(file_path, bucket_name, object_name)


# file_path = '/path/to/file.txt'
# bucket_name = 'your-bucket-name'
# object_name = 'file.txt'

# upload_to_s3(file_path, bucket_name, object_name)



folder_name = 'coco_original/'

# Create the folder
s3_client.put_object(Bucket=s3_settings.bucket_name, Key=folder_name)
