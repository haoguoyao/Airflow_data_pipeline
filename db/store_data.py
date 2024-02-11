from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey,JSON,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
Base = declarative_base()



class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    width = Column(Integer)
    height = Column(Integer)
    file_name = Column(String(255))
    license = Column(Integer, nullable=True)
    flickr_url = Column(String(255), nullable=True)
    coco_url = Column(String(255), nullable=True)
    date_captured = Column(DateTime, default=datetime.datetime.utcnow)

    annotations = relationship("Annotation", back_populates="image")

class Annotation(Base):
    __tablename__ = 'annotations'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'))
    category_id = Column(Integer)
    area = Column(Float)
    bbox = Column(String(255))  # Consider storing as JSON or creating separate columns
    iscrowd = Column(Integer)
    segmentation = Column(JSON)  # Use JSON for MySQL versions that support it

    image = relationship("Image", back_populates="annotations")
    category = relationship("Category", back_populates="annotations")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    supercategory = Column(String(50), nullable=True)

    annotations = relationship("Annotation", back_populates="category")


# Connect to your MySQL database
# Format: mysql+mysqlconnector://<user>:<password>@<host>/<dbname>
engine = create_engine('mysql+mysqlconnector://username:password@localhost/yourdatabase')
Base.metadata.create_all(engine)  # Creates tables if they don't already exist
Session = sessionmaker(bind=engine)
session = Session()

def store_annotations(annotations):
    for annotation in annotations:
        # Convert bbox list to a string for storage; you might choose a different method
        bbox_str = ','.join(map(str, annotation['bbox']))
        new_annotation = Annotation(
            id=annotation['id'],
            image_id=annotation['image_id'],
            category_id=annotation['category_id'],
            area=annotation['area'],
            bbox=bbox_str,
            iscrowd=annotation['iscrowd'],
            segmentation=annotation.get('segmentation', None)  # Assuming segmentation is optional
        )
        session.add(new_annotation)

    try:
        session.commit()
    except Exception as e:
        print(f"An error occurred while inserting annotations: {e}")
        session.rollback()
    finally:
        session.close()



def store_categories(categories):
    for category in categories:
        # Create a new Category object for each category in the list
        new_category = Category(
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
