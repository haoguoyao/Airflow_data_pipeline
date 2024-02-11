import csv
from pycocotools.coco import COCO

# Path to the COCO annotation file
annotation_file = '/path/to/annotations.json'

# Initialize COCO object
coco = COCO(annotation_file)

# Get all categories
categories = coco.loadCats(coco.getCatIds())

# Get all images
images = coco.loadImgs(coco.getImgIds())

# Create a CSV file
csv_file = '/path/to/output.csv'

# Open the CSV file in write mode
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(['image_id', 'category_id', 'bbox'])

    # Iterate over each image
    for image in images:
        image_id = image['id']

        # Get annotations for the image
        annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))

        # Iterate over each annotation
        for annotation in annotations:
            category_id = annotation['category_id']
            bbox = annotation['bbox']

            # Write the row to the CSV file
            writer.writerow([image_id, category_id, bbox])

print('CSV file created successfully.')
