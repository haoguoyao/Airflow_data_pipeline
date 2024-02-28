from typing import Union, List, Dict, Optional
from pydantic import BaseModel, validator, Field, root_validator
from db.db_models import (
    AnnotationDB,
    ImageDB,
    CategoryDB,
    Annotation_predictionDB,
    Image_predictionDB,
)
import datetime


class Category(BaseModel):
    id: int
    name: str
    supercategory: Optional[str] = None

    def model_dump_dict(self) -> dict:
        data = super().model_dump()
        return data


class AnnotationBox(BaseModel):
    x_min: float
    y_min: float
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

    def convert_annotation_box_to_string(self) -> str:
        return f"{self.x_min},{self.y_min},{self.width},{self.height}"


class AnnotationPrediction(BaseModel):
    id: int
    category_id: int
    crop_name: str
    bbox: AnnotationBox
    confidence: float
    image_name: str

    def convert_to_sql(self) -> Annotation_predictionDB:
        bbox_str = (
            f"{self.bbox.x_min},{self.bbox.y_min},{self.bbox.width},{self.bbox.height}"
        )

        return Annotation_predictionDB(
            id=self.id,
            category_id=self.category_id,
            crop_name=self.crop_name,
            bbox=bbox_str,
            confidence=self.confidence,
            image_name=self.image_name,
        )


class ImagePrediction(BaseModel):
    id: str  # Assuming id is the image name
    prediction: list
    annotations_prediction: List[AnnotationPrediction] = Field(default_factory=list)

    def convert_to_sql(self) -> Image_predictionDB:
        image_predictdb = Image_predictionDB(id=self.id, prediction=self.prediction)
        if self.annotations_prediction:
            image_predictdb.annotations_prediction = [
                ann.convert_annotation_to_sql() for ann in self.annotations_prediction
            ]
        return


class Annotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    iscrowd: Optional[int] = 0
    segmentation: Optional[Union[List, Dict]] = None
    area: Optional[float] = None
    bbox: AnnotationBox

    @validator("segmentation", always=True)
    def check_segmentation_type(cls, v, values):
        if values["iscrowd"] == 0 and not isinstance(v, List):
            raise ValueError("segmentation must be a List when iscrowd is 0")
        elif values["iscrowd"] == 1 and not isinstance(v, Dict):
            raise ValueError("segmentation must be a Dict when iscrowd is 1")
        return v

    @root_validator(pre=True)
    def calculate_area(cls, values):
        """
        Calculate the area from bbox if area is not explicitly provided.
        """
        bbox, area = values.get("bbox"), values.get("area")
        if bbox and area is None:
            # Assuming bbox is a dict with keys 'width' and 'height' if not already an AnnotationBox instance
            if not isinstance(bbox, AnnotationBox):
                bbox = AnnotationBox(**bbox)
            values["area"] = bbox.width * bbox.height
        return values

    def convert_annotation_to_sql(self) -> AnnotationDB:
        return AnnotationDB(
            id=self.id,
            image_id=self.image_id,
            category_id=self.category_id,
            area=self.area,
            bbox=self.bbox.convert_annotation_box_to_string(),
            iscrowd=self.iscrowd,
            segmentation=self.segmentation,
        )

    def model_dump_dict(self) -> dict:
        data = super().model_dump()
        bbox_data = data.pop("bbox")  # Remove 'bbox' and handle separately
        # Include bbox details as separate fields
        data["bbox_x_min"] = bbox_data["x_min"]
        data["bbox_y_min"] = bbox_data["y_min"]
        data["bbox_width"] = bbox_data["width"]
        data["bbox_height"] = bbox_data["height"]
        return data


class Image(BaseModel):
    id: int
    width: int
    height: int
    file_name: str
    license: Optional[int] = None
    flickr_url: Optional[str] = None
    coco_url: Optional[str] = None
    date_captured: Optional[str] = None
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
            date_captured=(
                datetime.datetime.fromisoformat(self.date_captured)
                if self.date_captured
                else None
            ),
        )

        # Convert annotations if they exist
        # TODO
        if self.annotations:
            image.annotations = [
                ann.convert_annotation_to_sql() for ann in self.annotations
            ]
        return image

    def convert_annotation_to_csv(self):
        csv_annotation = {
            "image_id": self.image_id,
            "category_id": self.category_id,
            **self.bbox.model_dump(),
        }


class COCODataset(BaseModel):
    images: List[Image]
    categories: List[Category]
