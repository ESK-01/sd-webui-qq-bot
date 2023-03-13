from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
from transformers import AutoFeatureExtractor
from PIL import Image
import numpy as np

# load safety model
safety_model_id = "CompVis/stable-diffusion-safety-checker"
safety_feature_extractor = None
safety_checker = None

def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    pil_images = [Image.fromarray(image) for image in images]

    return pil_images

def predict_image(x_image):
    global safety_feature_extractor, safety_checker
    if safety_feature_extractor is None:
        safety_feature_extractor = AutoFeatureExtractor.from_pretrained(safety_model_id)
        safety_checker = StableDiffusionSafetyChecker.from_pretrained(safety_model_id).to('cuda')
    safety_checker_input = safety_feature_extractor(x_image, return_tensors="pt").to('cuda')
    x_checked_image, has_nsfw_concept = safety_checker(images=np.array(x_image), clip_input=safety_checker_input.pixel_values)
    return x_checked_image, has_nsfw_concept