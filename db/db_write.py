
from pycocotools.coco import COCO
import db.db_models as db_models
import db.db_connections as db_connections


def write_from_annotation(annotation_file):
    coco = COCO(annotation_file)

    categories = coco.loadCats(coco.getCatIds())
    store_from_original = db_models.Store_from_original()
    store_from_original.store_categories(categories,db_connections.get_db_session())
    print("Categories stored successfully")

    imgs = coco.loadImgs(coco.getImgIds())
    store_from_original.store_images(imgs,db_connections.get_db_session())
    print("Images stored successfully")

    anns = coco.loadAnns(coco.getAnnIds())
    store_from_original.store_annotations(anns,db_connections.get_db_session())
    print("Annotations stored successfully")


if __name__ == "__main__":
    db_models.empty_tables(db_connections.get_db_session())
    annotation_file = '/Users/hao/Downloads/annotations/instances_val2017.json'
    write_from_annotation(annotation_file)
    print("Original annotation written to database successfully")

