from typing import List, Optional
from pydantic import BaseModel, validator, Field
from db.db_models import AnnotationDB, ImageDB, CategoryDB
import datetime
class Category(BaseModel):
    id: int
    name: str
    supercategory: Optional[str] = None

class AnnotationBox(BaseModel):
    x_min: float
    y_min: float
    width: float
    height: float

    def convert_annotation_box_to_string(self) -> str:
        return f"{self.x_min},{self.y_min},{self.width},{self.height}"


class Annotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    segmentation: Optional[List] = None
    area: float
    bbox: AnnotationBox
    iscrowd: int

    def convert_annotation_to_sql(self) -> AnnotationDB:
        return AnnotationDB(
            id=self.id,
            image_id=self.image_id,
            category_id=self.category_id,
            area=self.area,
            bbox=self.bbox.convert_annotation_box_to_string(),
            iscrowd=self.iscrowd,
            segmentation=self.segmentation
        )
    def convert_annotation_to_csv(self):
        csv_annotation = {
        'image_id': self.image_id,
        'file_name': file_name,
        'category_id': self.category_id,
        **self.bbox.model_dump(),
    }


class Image(BaseModel):
    id: int
    width: int
    height: int
    file_name: str
    license: Optional[int]= None
    flickr_url: Optional[str]= None
    coco_url: Optional[str]= None
    date_captured: Optional[str]= None
    annotations: List[Annotation] = Field(default_factory=list)

    def convert_image_to_sql(self) -> ImageDB:
        """
        Convert an Image Pydantic model to an SQLAlchemy Image model.
        """
        image = ImageDB(
            id=self.id,
            width=self.width,
            height=self.height,
            file_name=self.file_name,
            license=self.license,
            flickr_url=self.flickr_url,
            coco_url=self.coco_url,
            date_captured=datetime.datetime.fromisoformat(self.date_captured) if self.date_captured else None
        )
        
        # Convert annotations if they exist
        if self.annotations:
            image.annotations = [ann.convert_annotation_to_sql() for ann in self.annotations]
        
        return image


class COCODataset(BaseModel):
    images: List[Image]
    categories: List[Category]


def convert_annotation_box_from_sql_to_pydantic(bbox_str):
    """
    Converts a bounding box string from the database to a Pydantic model.
    Assume bbox_str is a comma-separated string: "x_min,y_min,width,height"
    """
    x_min, y_min, width, height = map(float, bbox_str.split(','))
    return AnnotationBox(x_min=x_min, y_min=y_min, width=width, height=height)

def convert_annotation_from_sql_to_pydantic(annotation):
    """
    Convert a single SQLAlchemy Annotation instance to a Pydantic model.
    """
    bbox = convert_annotation_box_from_sql_to_pydantic(annotation.bbox)
    return Annotation(
        id=annotation.id,
        image_id=annotation.image_id,
        category_id=annotation.category_id,
        segmentation=annotation.segmentation,
        area=annotation.area,
        bbox=bbox,
        iscrowd=annotation.iscrowd
    )

def convert_image_from_sql_to_pydantic(image):
    """
    Convert a single SQLAlchemy Image instance to a Pydantic model.
    """
    annotations = [convert_annotation_from_sql_to_pydantic(ann) for ann in image.annotations]
    return Image(
        id=image.id,
        width=image.width,
        height=image.height,
        file_name=image.file_name,
        license=image.license,
        flickr_url=image.flickr_url,
        coco_url=image.coco_url,
        date_captured=image.date_captured.isoformat() if image.date_captured else None,
        annotations=annotations
    )
