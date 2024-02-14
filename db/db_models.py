from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey,JSON,DateTime,BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import db.db_connections as db_connection

import datetime


Base = declarative_base()

class ImageDB(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    width = Column(Integer)
    height = Column(Integer)
    file_name = Column(String(255))
    license = Column(Integer, nullable=True)
    flickr_url = Column(String(255), nullable=True)
    coco_url = Column(String(255), nullable=True)
    date_captured = Column(DateTime, default=datetime.datetime.utcnow)

    annotations = relationship("AnnotationDB", back_populates="image")



class AnnotationDB(Base):
    __tablename__ = 'annotations'
    id = Column(BigInteger, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    area = Column(Float)
    bbox = Column(String(255))  # Consider storing as JSON or creating separate columns
    iscrowd = Column(Integer)
    segmentation = Column(JSON)  # Use JSON for MySQL versions that support it

    image = relationship("ImageDB", back_populates="annotations")
    category = relationship("CategoryDB", back_populates="annotations")


class CategoryDB(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    supercategory = Column(String(50), nullable=True)

    annotations = relationship("AnnotationDB", back_populates="category")


def create_tables():
    engine = db_connection.get_db_engine()
    Base.metadata.create_all(engine)  # Creates tables if they don't already exist
class Store_from_original:
    def store_annotations(self,annotations,session,batch_size=1000):
        batch = []
        for i, annotation in enumerate(annotations, 1):
            bbox_str = ','.join(map(str, annotation['bbox']))
            new_annotation = AnnotationDB(
                id=annotation['id'],
                image_id=annotation['image_id'],
                category_id=annotation['category_id'],
                area=annotation['area'],
                bbox=bbox_str,
                iscrowd=annotation['iscrowd'],
                segmentation=annotation.get('segmentation', None)  # Assuming segmentation is optional
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

    def store_images(self,images,session):
        for image in images:
            new_image = ImageDB(
                id=image['id'],
                width=image['width'],
                height=image['height'],
                file_name=image['file_name'],
                license=image.get('license', None),
                flickr_url=image.get('flickr_url', None),
                coco_url=image.get('coco_url', None),
                date_captured=image.get('date_captured', None)
            )
            session.add(new_image)

        try:
            session.commit()
        except Exception as e:
            print(f"An error occurred while inserting images: {e}")
            session.rollback()
        finally:
            session.close()

    def store_categories(self,categories,session):
        for category in categories:
            # Create a new Category object for each category in the list
            new_category = CategoryDB(
                id=category["id"],
                name=category["name"],
                supercategory=category.get("supercategory")  # .get() returns None if 'supercategory' doesn't exist
            )
            session.add(new_category)  # Add the new Category object to the session

        try:
            session.commit()  # Attempt to commit all the changes to the database
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()  # Roll back the changes on error
        finally:
            session.close()  # Close the session whether or not an error occurred

def empty_tables(session):
    session.query(AnnotationDB).delete()
    session.query(ImageDB).delete()
    session.query(CategoryDB).delete()
    session.commit()
    session.close()
