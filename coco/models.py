from typing import List, Optional
from pydantic import BaseModel

class Category(BaseModel):
    id: int
    name: str
    supercategory: Optional[str] = None

class Annotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    segmentation: Optional[List] = None
    area: float
    bbox: List[float]
    iscrowd: int

class Image(BaseModel):
    id: int
    width: int
    height: int
    file_name: str
    license: Optional[int]= None
    flickr_url: Optional[str]= None
    coco_url: Optional[str]= None
    date_captured: Optional[str]= None

class COCODataset(BaseModel):
    images: List[Image]
    annotations: List[Annotation]
    categories: List[Category]
