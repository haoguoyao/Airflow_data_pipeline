from pycocotools.coco import COCO
import db.db_models as db_models
import db.db_connections as db_connections
from db.db_settings import coco_val_annotation_file
from db.db_connections import get_db_session
from db.db_models import ImageDB, CategoryDB, AnnotationDB
from sqlalchemy import func
import coco.coco_models as coco_models
from sqlalchemy import func
from typing import Type, List
from pydantic import BaseModel
from db.db_models import ConvertibleToPydantic


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


def get_random_objects_from_db(
    model_class: Type[ConvertibleToPydantic], size: int
) -> List[BaseModel]:
    session = get_db_session()
    # Ensure that the model_class actually refers to an SQLAlchemy model with the expected class method
    random_objects = session.query(model_class).order_by(func.rand()).limit(size).all()
    converted_objects = [
        model_class.convert_from_sql_to_pydantic(an_object)
        for an_object in random_objects
    ]
    session.close()
    return converted_objects


def get_fields_from_db(model_field) -> List:
    session = get_db_session()
    objects = session.query(model_field).all()
    object_lst = [an_object[0] for an_object in objects]
    session.close()
    return object_lst


def get_objects_in_batches_from_db(
    model_class: Type[ConvertibleToPydantic], batch_size: int = 5000
) -> List[BaseModel]:
    session = get_db_session()
    total_count = session.query(func.count(model_class.id)).scalar()
    batches = total_count // batch_size + (1 if total_count % batch_size else 0)

    all_converted_objects = []

    for batch in range(batches):
        offset = batch * batch_size
        # Adjust this query if your database does not support OFFSET and LIMIT for batch processing
        random_objects = (
            session.query(model_class).limit(batch_size).offset(offset).all()
        )
        converted_objects = [
            model_class.convert_from_sql_to_pydantic(obj) for obj in random_objects
        ]
        all_converted_objects.extend(converted_objects)

    session.close()
    return all_converted_objects


def get_random_objects_from_db(
    model_class: Type[ConvertibleToPydantic], size: int
) -> List[BaseModel]:
    session = get_db_session()
    # Ensure that the model_class actually refers to an SQLAlchemy model with the expected class method
    random_objects = session.query(model_class).order_by(func.rand()).limit(size).all()
    converted_objects = [
        model_class.convert_from_sql_to_pydantic(an_object)
        for an_object in random_objects
    ]
    session.close()
    return converted_objects


def query_images_by_filenames(file_names: list):
    session = get_db_session()
    images = session.query(ImageDB).filter(ImageDB.file_name.in_(file_names)).all()
    converted_objects = [
        ImageDB.convert_from_sql_to_pydantic(an_object) for an_object in images
    ]
    session.close()
    return converted_objects


if __name__ == "__main__":
    # test write everything from annotation file to database
    db_models.delete_tables()
    db_models.create_tables()

    write_from_annotation(coco_val_annotation_file)
    print("Original annotation written to database successfully")
