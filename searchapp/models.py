# searchapp/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import torch
from transformers import CLIPProcessor, CLIPModel
from qdrant_client import QdrantClient
import numpy as np
import requests
from PIL import Image
from io import BytesIO

# Load the CLIP model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("models/clip-vit-base-patch32",local_files_only=True).to(device)
clip_processor = CLIPProcessor.from_pretrained("models/clip-vit-base-patch32",local_files_only=True)

# Initialize Qdrant client
qdrant_client = QdrantClient(url="efd9ea28-a235-417e-b78f-cb7eeef3e56a.hsvc.ir:32621")

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    material = models.CharField(max_length=255, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    brand_id = models.IntegerField(null=True, blank=True)
    brand_name = models.CharField(max_length=255, null=True, blank=True)
    category_id = models.IntegerField(null=True, blank=True)
    category_name = models.CharField(max_length=255, null=True, blank=True)
    gender_id = models.IntegerField(null=True, blank=True)
    gender_name = models.CharField(max_length=255, null=True, blank=True)
    shop_id = models.IntegerField()
    shop_name = models.CharField(max_length=255)
    link = models.URLField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=50)
    colors = models.JSONField(null=True, blank=True)
    sizes = models.JSONField(null=True, blank=True)
    region = models.CharField(max_length=100)
    currency = models.CharField(max_length=10)
    current_price = models.FloatField()
    old_price = models.FloatField(null=True, blank=True)
    off_percent = models.FloatField(null=True, blank=True)
    update_date = models.DateTimeField()
    name_embedding = models.BinaryField(null=True, blank=True) 
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=200)
    image_embedding = models.BinaryField(null=True, blank=True)  # Store the image embedding as binary data

    def __str__(self):
        return f"{self.product.name} Image"

@receiver(post_save, sender=Product)
def encode_product_name(sender, instance, **kwargs):
    if instance.name and not instance.name_embedding:
        try:
            # Encode the product name with CLIP model
            inputs = clip_processor(text=[instance.name], return_tensors="pt", padding=True, truncation=True).to(device)
            with torch.no_grad():
                name_features = clip_model.get_text_features(**inputs).cpu().numpy()

            # Save the name embedding to the model
            instance.name_embedding = name_features.tobytes()
            instance.save()

            # Save the name embedding to Qdrant
            qdrant_client.upload_collection(
                collection_name="product_titles",
                vectors=np.array([name_features[0]]),
                payload=[{"product_id": instance.id, "name": instance.name}],
            )
            print(f"Uploaded name embedding for product ID {instance.id} to Qdrant.")
        except Exception as e:
            print(f"Error encoding product name for product ID {instance.id}: {e}")

@receiver(post_save, sender=ProductImage)
def encode_image(sender, instance, **kwargs):
    if instance.image_url and not instance.image_embedding:
        try:
            # Encode the image with CLIP model
            response = requests.get(instance.image_url)
            response.raise_for_status()  # Ensure the request was successful
            image = Image.open(BytesIO(response.content))

            inputs = clip_processor(images=image, return_tensors="pt").to(device)
            with torch.no_grad():
                image_features = clip_model.get_image_features(**inputs).cpu().numpy()

            # Save the image embedding to the model
            instance.image_embedding = image_features.tobytes()
            instance.save()

            # Save the image embedding to Qdrant
            qdrant_client.upload_collection(
                collection_name="product_images",
                vectors=np.array([image_features[0]]),
                payload=[{"product_id": instance.product.id, "image_url": instance.image_url}],
            )
            print(f"Uploaded image embedding for product ID {instance.product.id} to Qdrant.")
        except Exception as e:
            print(f"Error encoding image for product ID {instance.product.id}: {e}")