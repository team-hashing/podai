from vertexai.preview.vision_models import Image, ImageGenerationModel
from PIL import Image as PILImage  # Import the PIL module

def generate_image(name: str):
    try:
        img_generation_model = ImageGenerationModel.from_pretrained("imagegeneration@005")
        
        prompt = f"High resolution image of {name}"
        images = img_generation_model.generate_images(
            prompt=prompt,
            number_of_images=1,
        )
        
        image = images[0]
        return image
    except Exception as e:
        print(f"An error occurred during image generation: {e}")
        return None