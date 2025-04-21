from deepface import DeepFace
from pprint import pprint
import numpy as np
import cv2

def convert_numpy_types(obj):
    """
    Recursively convert all numpy types to native Python types
    for cleaner display.
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
def preprocess_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, (800, 800))  # safe working size
    return img

def get_emotion(img_path):
    img = preprocess_image(img_path)
    result = DeepFace.analyze(img, detector_backend="ssd", actions=["emotion"])
    if isinstance(result, list):
        result = result[0]  # take the first detected face
    return result["dominant_emotion"]

def main():
    result = get_emotion("distressed-angry-bearded-redhead-guy-posing-against-white-wall.jpg")
    pprint(result, sort_dicts=False)

if __name__ == "__main__":
    main()