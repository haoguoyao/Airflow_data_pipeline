from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    JSON,
    DateTime,
    BigInteger,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import db.db_connections as db_connection
from abc import ABCMeta, ABC, abstractmethod
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from pydantic import BaseModel
import datetime
import json


# Step 1: Create a compatible metaclass
class CustomMeta(DeclarativeMeta, ABCMeta):
    pass


# Step 2: Define a common base class using the compatible metaclass
Base = declarative_base(metaclass=CustomMeta)


class ConvertibleToPydantic(ABC):
    @classmethod
    @abstractmethod
    def convert_from_sql_to_pydantic(cls, db_object) -> BaseModel:
        pass


class CategoryDB(Base, ConvertibleToPydantic):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    supercategory = Column(String(50), nullable=True)
    annotations = relationship("AnnotationDB", back_populates="category")
    annotation_predictions = relationship(
        "Annotation_predictionDB", back_populates="category"
    )

    @classmethod
    def convert_from_sql_to_pydantic(cls, category):
        from coco.coco_models import Category

        return Category(
            id=category.id, name=category.name, supercategory=category.supercategory
        )


class ImageDB(Base, ConvertibleToPydantic):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    width = Column(Integer)
    height = Column(Integer)
    file_name = Column(String(255), unique=True, nullable=False)
    license = Column(Integer, nullable=True)
    flickr_url = Column(String(255), nullable=True)
    coco_url = Column(String(255), nullable=True)
    date_captured = Column(DateTime, default=datetime.datetime.utcnow)

    annotations = relationship("AnnotationDB", back_populates="image")

    @classmethod
    def convert_from_sql_to_pydantic(cls, image):
        from coco.coco_models import Image

        annotations = [
            AnnotationDB.convert_from_sql_to_pydantic(ann) for ann in image.annotations
        ]
        return Image(
            id=image.id,
            width=image.width,
            height=image.height,
            file_name=image.file_name,
            license=image.license,
            flickr_url=image.flickr_url,
            coco_url=image.coco_url,
            date_captured=(
                image.date_captured.isoformat() if image.date_captured else None
            ),
            annotations=annotations,
        )


class AnnotationDB(Base, ConvertibleToPydantic):
    __tablename__ = "annotations"
    id = Column(BigInteger, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    area = Column(Float)
    bbox = Column(String(255))
    iscrowd = Column(Integer)
    segmentation = Column(JSON)

    image = relationship("ImageDB", back_populates="annotations")
    category = relationship("CategoryDB", back_populates="annotations")

    @classmethod
    def convert_annotation_box_from_sql_to_pydantic(cls, bbox_str) -> BaseModel:
        from coco.coco_models import AnnotationBox

        x_min, y_min, width, height = map(float, bbox_str.split(","))
        return AnnotationBox(x_min=x_min, y_min=y_min, width=width, height=height)

    @classmethod
    def convert_from_sql_to_pydantic(cls, annotation) -> BaseModel:
        from coco.coco_models import Annotation

        bbox = AnnotationDB.convert_annotation_box_from_sql_to_pydantic(annotation.bbox)
        return Annotation(
            id=annotation.id,
            image_id=annotation.image_id,
            category_id=annotation.category_id,
            segmentation=annotation.segmentation,
            area=annotation.area,
            bbox=bbox,
            iscrowd=annotation.iscrowd,
        )


class Image_predictionDB(Base, ConvertibleToPydantic):
    __tablename__ = "images_prediction"

    # id is image name
    id = Column(String(255), primary_key=True)
    prediction = Column(JSON)
    annotations_predictions = relationship(
        "Annotation_predictionDB", back_populates="image_prediction"
    )

    @classmethod
    def convert_from_sql_to_pydantic(cls, db_object) -> BaseModel:
        if not isinstance(db_object, Image_predictionDB):
            raise ValueError(
                f"db_object must be an instance of Image_predictionDB, got {type(db_object)} instead."
            )
        from coco.coco_models import ImagePrediction

        annotations = [
            Annotation_predictionDB.convert_from_sql_to_pydantic(ann)
            for ann in db_object.annotations_predictions
        ]
        return ImagePrediction(
            id=db_object.id,
            prediction=json.loads(db_object.prediction),
            annotations_prediction=annotations,
        )


class Annotation_predictionDB(Base, ConvertibleToPydantic):
    __tablename__ = "annotations_predictions"
    id = Column(BigInteger, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    crop_name = Column(String(255))
    bbox = Column(String(255))
    confidence = Column(Float)
    image_name = Column(String(255), ForeignKey("images_prediction.id"), nullable=False)
    image_prediction = relationship(
        "Image_predictionDB", back_populates="annotations_predictions"
    )
    category = relationship("CategoryDB", back_populates="annotation_predictions")

    @classmethod
    def convert_annotation_box_from_sql_to_pydantic(cls, bbox_str) -> BaseModel:
        bbox_str = json.loads(bbox_str)
        from coco.coco_models import AnnotationBox

        # return AnnotationBox(x_min=bbox_str[0], y_min=bbox_str[1], width=bbox_str[2]-bbox_str[0], height=bbox_str[3]-bbox_str[1])
        return AnnotationBox(
            x_min=bbox_str[0], y_min=bbox_str[1], width=bbox_str[2], height=bbox_str[3]
        )

    @classmethod
    def convert_from_sql_to_pydantic(cls, db_object) -> BaseModel:
        from coco.coco_models import AnnotationPrediction

        bbox = cls.convert_annotation_box_from_sql_to_pydantic(db_object.bbox)
        return AnnotationPrediction(
            id=db_object.id,
            category_id=db_object.category_id,
            crop_name=db_object.crop_name,
            bbox=bbox,
            confidence=db_object.confidence,
            image_name=db_object.image_name,
        )


def store_one_db_object(object):
    session = db_connection.get_db_session()
    session.add(object)
    session.commit()
    session.close()


def store_db_objects(objects):
    session = db_connection.get_db_session()
    for object in objects:
        session.add(object)
    session.commit()
    session.close()


# def store_one_annotation_prediction(annotation_prediction):
#     session = db_connection.get_db_session()
#     new_annotation_prediction = Annotation_predictionDB(
#         category_id=annotation_prediction['category_id'],
#         crop_name=annotation_prediction['crop_name'],
#         bbox=annotation_prediction['bbox'],
#         confidence=annotation_prediction['confidence'],
#         image_name=annotation_prediction['image_name']
#     )
#     session.add(new_annotation_prediction)
#     session.commit()
#     session.close()


def store_one_image_prediction(image_prediction):
    prediction_data = [
        prediction.tolist() for prediction in image_prediction["prediction"]
    ]
    prediction_JSON = json.dumps(prediction_data)

    session = db_connection.get_db_session()
    new_image_prediction = Image_predictionDB(
        id=image_prediction["file_name"], prediction=prediction_JSON
    )
    session.add(new_image_prediction)

    try:
        session.commit()
    except Exception as e:
        print(f"An error occurred while inserting image predictions: {e}")
        session.rollback()
    finally:
        session.close()


class Store_from_original:
    def store_annotations(self, annotations, batch_size=1000):
        session = db_connection.get_db_session()
        batch = []
        for i, annotation in enumerate(annotations, 1):
            bbox_str = ",".join(map(str, annotation["bbox"]))
            new_annotation = AnnotationDB(
                id=annotation["id"],
                image_id=annotation["image_id"],
                category_id=annotation["category_id"],
                area=annotation["area"],
                bbox=bbox_str,
                iscrowd=annotation["iscrowd"],
                segmentation=annotation.get(
                    "segmentation", None
                ),  # Assuming segmentation is optional
            )
            batch.append(new_annotation)

            if i % batch_size == 0:
                session.bulk_save_objects(batch)
                session.commit()
                batch = []  # Reset the batch

        # Insert any remaining annotations
        if batch:
            session.bulk_save_objects(batch)
            session.commit()
        session.close()

    def store_images(self, images):
        session = db_connection.get_db_session()
        for image in images:
            new_image = ImageDB(
                id=image["id"],
                width=image["width"],
                height=image["height"],
                file_name=image["file_name"],
                license=image.get("license", None),
                flickr_url=image.get("flickr_url", None),
                coco_url=image.get("coco_url", None),
                date_captured=image.get("date_captured", None),
            )
            session.add(new_image)

        try:
            session.commit()
        except Exception as e:
            print(f"An error occurred while inserting images: {e}")
            session.rollback()
        finally:
            session.close()

    def store_categories(self, categories):
        session = db_connection.get_db_session()
        for category in categories:
            # Create a new Category object for each category in the list
            new_category = CategoryDB(
                id=category["id"],
                name=category["name"],
                supercategory=category.get(
                    "supercategory"
                ),  # .get() returns None if 'supercategory' doesn't exist
            )
            session.add(new_category)  # Add the new Category object to the session

        try:
            session.commit()  # Attempt to commit all the changes to the database
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()  # Roll back the changes on error
        finally:
            session.close()  # Close the session whether or not an error occurred


def create_tables():
    engine = db_connection.get_db_engine()
    Base.metadata.create_all(engine)  # Creates tables if they don't already exist


def delete_tables():
    engine = db_connection.get_db_engine()
    Base.metadata.reflect(engine)
    Base.metadata.drop_all(engine)


def empty_tables():
    session = db_connection.get_db_session()
    session.query(AnnotationDB).delete()
    session.query(ImageDB).delete()
    session.query(CategoryDB).delete()
    session.query(Image_predictionDB).delete()
    session.query(Annotation_predictionDB).delete()
    session.commit()
    session.close()
    return

def empty_prediction_tables():

    session = db_connection.get_db_session()
    session.query(Annotation_predictionDB).delete()
    session.query(Image_predictionDB).delete()
    session.commit()
    session.close()
    return

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully")
