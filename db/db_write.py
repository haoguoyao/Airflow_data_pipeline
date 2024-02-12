
from pycocotools.coco import COCO
import db.db_models as db_models
import db.db_connections as db_connections


def write_from_annotation(annotation_file):
    coco = COCO(annotation_file)

    categories = coco.loadCats(coco.getCatIds())
    db_models.store_categories(categories,db_connections.get_db_session())

    imgs = coco.loadImgs(coco.getImgIds())
    db_models.store_images(imgs,db_connections.get_db_session())

    anns = coco.loadAnns(coco.getAnnIds())
    db_models.store_annotations(anns,db_connections.get_db_session())


if __name__ == "__main__":
    db_models.empty_tables(db_connections.get_db_session())
    annotation_file = '/Users/hao/Downloads/annotations/instances_val2017.json'
    write_from_annotation(annotation_file)
    print("Data loaded successfully")

