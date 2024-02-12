from coco.coco_models import COCODataset
import json
from pydantic import ValidationError

# Load COCO data from a file
with open('path_to_your_coco_data.json') as f:
    coco_data = json.load(f)

# Validate COCO data
try:
    validated_data = COCODataset(**coco_data)
except ValidationError as e:
    print(e)
