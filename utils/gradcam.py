import numpy as np
import tensorflow as tf
from PIL import Image
import cv2
import io

def generate_gradcam(model, img_array, class_idx):
    last_conv_layer = None
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_layer = layer.name
            break

    grad_model = tf.keras.models.Model(
        inputs=model.input,
        outputs=[model.get_layer(last_conv_layer).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, class_idx]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    heatmap = heatmap.numpy()

    heatmap = cv2.resize(heatmap, (224, 224))
    heatmap = np.uint8(255 * heatmap)
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    return heatmap_colored

def overlay_heatmap(original_pil, heatmap_colored, alpha=0.4):
    original_np = np.array(original_pil.resize((224, 224)))
    overlay = cv2.addWeighted(original_np, 1 - alpha, heatmap_colored, alpha, 0)
    return Image.fromarray(overlay)

def pil_to_bytes(pil_image):
    buf = io.BytesIO()
    pil_image.save(buf, format='PNG')
    return buf.getvalue()
