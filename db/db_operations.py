
from pycocotools.coco import COCO
import db.db_models as db_models
import db.db_connections as db_connections
from db.db_settings import coco_val_annotation_file
from db.db_connections import get_db_session
from db.db_models import ImageDB,CategoryDB
from sqlalchemy import func
import coco.coco_models as coco_models
# def get_category_id_map(categories):
#     category_id_map = {}
#     for category in categories:
#         category_id_map[category['id']] = category['name']
#     return category_id_map

def write_from_annotation(annotation_file):
    coco = COCO(annotation_file)

    categories = coco.loadCats(coco.getCatIds())
    store_from_original = db_models.Store_from_original()
    store_from_original.store_categories(categories)
    print("Categories stored successfully")

    imgs = coco.loadImgs(coco.getImgIds())
    store_from_original.store_images(imgs)
    print("Images stored successfully")

    anns = coco.loadAnns(coco.getAnnIds())
    store_from_original.store_annotations(anns)
    print("Annotations stored successfully")

def get_random_images(numb_images):
    session = get_db_session()
    random_images = session.query(ImageDB).order_by(func.rand()).limit(numb_images).all()
    images = [coco_models.convert_image_from_sql_to_pydantic(image) for image in random_images]
    return images
def get_categories():
    session = get_db_session()
    categories = session.query(CategoryDB).all()
    categories = [coco_models.convert_category_from_sql_to_pydantic(category) for category in categories]
    return categories


if __name__ == "__main__":
    # # test write everything from annotation file to database
    # db_models.empty_tables(db_connections.get_db_session())
    # write_from_annotation(coco_val_annotation_file)
    # print("Original annotation written to database successfully")

    categories = get_categories()
    print(categories)
 

