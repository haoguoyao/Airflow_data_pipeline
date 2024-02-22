
import csv
from db.db_connections import get_db_session
from db.db_models import ImageDB, AnnotationDB,CategoryDB
from sqlalchemy import func
from s3.s3_access import download_image_from_s3
import matplotlib.pyplot as plt
import os
import csv
import pandas as pd

def csv_helper(csv_output_path,model_class, batch_size=1000):
    session = get_db_session()
    offset = 0
    first_batch = True
    if os.path.exists(csv_output_path):
        os.remove(csv_output_path)

    while True:
        # Query a batch of records from the specified model_class
        records = session.query(model_class).offset(offset).limit(batch_size).all()

        # Break the loop if no more records are found
        if not records:
            break

        # Process the batch using the provided conversion function
        annotations = [model_class.convert_from_sql_to_pydantic(record).model_dump_dict() for record in records]

        # Write the batch to CSV
        with open(csv_output_path, 'a', newline='') if not first_batch else open(csv_output_path, 'w', newline='') as csvfile:
            fieldnames = annotations[0].keys() if annotations else None
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if first_batch and fieldnames:
                writer.writeheader()
                first_batch = False

            writer.writerows(annotations)

        # Prepare for the next batch
        offset += batch_size
    session.close()


def generate_csv_from_db():
    csv_output_path = 'coco_annotations.csv'
    # Pass the conversion function as an argument to csv_helper
    csv_helper(csv_output_path, AnnotationDB)
    csv_output_path = 'coco_categories.csv'
    # Pass the conversion function as an argument to csv_helper
    csv_helper(csv_output_path,CategoryDB)

if __name__ == "__main__":

    file_path = 'coco_annotations.csv'
    df = pd.read_csv(file_path)
    print(df.head())
    print(df.info())
    print(df.describe())

    category_counts = df['category_id'].value_counts()
    print(category_counts)
    plt.figure(figsize=(25, 8))  
    category_counts.plot(kind='bar')
    plt.title('Category Counts') 
    plt.xlabel('Category ID')   
    plt.ylabel('Counts')         
    plt.savefig('category_counts.png')
    plt.close()

