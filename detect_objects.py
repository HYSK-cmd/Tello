import os
import io
from google.cloud import vision
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'google_cloud/vision_key.json'
def vision_detect(image_path):
    vision_client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        image_content = image_file.read()
    image = vision.Image(content=image_content)
    response = vision_client.object_localization(image=image)
    localized_object_annotations = response.localized_object_annotations
    obj_list = []
    for obj in localized_object_annotations:
        vertices = obj.bounding_poly.normalized_vertices
        x_coords = [v.x for v in vertices]
        y_coords = [v.y for v in vertices]
        bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
        obj_list.append({
            'object': obj.name,
            'score': obj.score,
            'bbox': bbox,
        })
    return obj_list
