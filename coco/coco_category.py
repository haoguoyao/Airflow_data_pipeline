import csv
from pycocotools.coco import COCO

from db.db_connections import get_db_connection


if __name__=="__main__":
    annotation_file = '/Users/hao/Downloads/annotations/instances_val2017.json'

    # Initialize COCO object
    coco = COCO(annotation_file)

    # Get all categories
    categories = coco.loadCats(coco.getCatIds())
    #{"supercategory": "person", "id": 1, "name": "person}


    conn = get_db_connection()
    cursor = conn.cursor()

    # Iterate over categories and insert into the database
    for category in categories:
        supercategory = category['supercategory']
        category_id = category['id']
        name = category['name']
        
        # Execute the insert query
        cursor.execute("INSERT INTO category (supercategory, id, name) VALUES (%s, %s, %s);", (supercategory, category_id, name))

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and database connection
    conn.close()
    cursor.close()