import numpy as np
from PIL import Image
import io

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
    return img_array, image

def is_likely_leaf(predictions, threshold=0.85):
    top_confidence = float(np.max(predictions))
    return top_confidence > 0.10

def get_severity(confidence):
    if confidence >= 0.85:
        return 'Severe', '#DC2626'
    elif confidence >= 0.60:
        return 'Moderate', '#F59E0B'
    else:
        return 'Low', '#16A34A'

def get_top3(predictions, class_names):
    top3_idx = np.argsort(predictions[0])[::-1][:3]
    top3 = []
    for idx in top3_idx:
        top3.append({
            'class': class_names[idx],
            'confidence': float(predictions[0][idx])
        })
    return top3

def format_disease_name(raw_name):
    parts = raw_name.split('___')
    if len(parts) == 2:
        crop = parts[0].replace('_', ' ').replace('(maize)', '(Maize)').replace('Pepper,', 'Pepper').replace(' bell', '').strip()
        disease = parts[1].replace('_', ' ').strip()
        return crop, disease
    return raw_name, raw_name
