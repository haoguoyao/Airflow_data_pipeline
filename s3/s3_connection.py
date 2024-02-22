import boto3
import s3.s3_settings as s3_settings

class S3Connection:
    _instance = None
    _s3_client = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(S3Connection, cls).__new__(cls)
            # Initialize the S3 client here
            cls._instance._initialize_s3_client(aws_access_key_id=s3_settings.aws_access_key_id,aws_secret_access_key=s3_settings.aws_secret_access_key,region_name=s3_settings.region_name)
        return cls._instance

    def _initialize_s3_client(self,aws_access_key_id,aws_secret_access_key,region_name):
        """Initialize the S3 client with the provided credentials."""
        if not self._s3_client:
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )

    @classmethod
    def get_s3_client(cls):
        """Returns the S3 client if it exists, or None otherwise."""
        if cls._instance:
            return cls._instance._s3_client
        else:
            return None
s3 = S3Connection()
s3_client = S3Connection.get_s3_client()


if __name__=="__main__":    
    s3_client = S3Connection.get_s3_client()
    if s3_client:
        print("S3 client initialized successfully.")
    else:
        print("S3 client initialization failed.")
    # import boto3
    # from urllib.parse import urlparse

    # def download_s3_file(s3_url, local_path):
    #     # Parse the S3 URL to extract bucket name and object key
    #     parsed_url = urlparse(s3_url)
    #     bucket_name = parsed_url.netloc
    #     object_key = parsed_url.path.lstrip('/')
        
    #     # Create an S3 client

    #     # Download the file from S3
    #     print(object_key)
    #     print(bucket_name)
    #     try:
    #         s3_client.download_file(bucket_name, object_key, local_path)
    #         print(f"File downloaded successfully to {local_path}")
    #     except Exception as e:
    #         print(f"Error downloading file: {e}")

    # # Example usage
    # s3_url = "s3://coco2024/coco_original/train2017/000000000009.jpg"
    # local_path = "/Users/hao/Desktop/github/a.jpg"
    # download_s3_file(s3_url, local_path)
