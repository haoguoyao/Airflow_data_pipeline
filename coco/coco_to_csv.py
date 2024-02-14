
import csv
from db.db_connections import get_db_session
from db.db_models import ImageDB, AnnotationDB,CategoryDB
from sqlalchemy import func
from s3.s3_access import download_image_from_s3
from coco.coco_models import Image, convert_category_from_sql_to_pydantic,Annotation, convert_annotation_from_sql_to_pydantic
import os
import csv
import os

def csv_helper(csv_output_path, session, model_class, conversion_function, batch_size=1000):
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
        annotations = [conversion_function(record).model_dump_dict() for record in records]

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


# Usage example
if __name__ == "__main__":
    session = get_db_session()  # Assume this function gets your DB session
    csv_output_path = 'coco_annotations.csv'
    # Pass the conversion function as an argument to csv_helper
    csv_helper(csv_output_path, session, AnnotationDB, convert_annotation_from_sql_to_pydantic)
    csv_output_path = 'coco_categories.csv'
    # Pass the conversion function as an argument to csv_helper
    csv_helper(csv_output_path, session, CategoryDB, convert_category_from_sql_to_pydantic)

