from transformers import CLIPProcessor, CLIPModel

# Specify the model name
model_name = "openai/clip-vit-base-patch32"

# Download the model and processor
clip_model = CLIPModel.from_pretrained(model_name)
clip_processor = CLIPProcessor.from_pretrained(model_name)

# Save the model locally
clip_model.save_pretrained('./models/clip-vit-base-patch32')
clip_processor.save_pretrained('./models/clip-vit-base-patch32')