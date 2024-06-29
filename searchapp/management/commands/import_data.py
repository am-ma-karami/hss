# searchapp/management/commands/import_data.py

import json
from django.core.management.base import BaseCommand
from searchapp.models import Product, ProductImage
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from datetime import datetime

class Command(BaseCommand):
    help = 'Import products and images from config.json'

    def handle(self, *args, **kwargs):
        with open('config.json') as f:
            data = json.load(f)

        qdrant_client = QdrantClient(url="efd9ea28-a235-417e-b78f-cb7eeef3e56a.hsvc.ir:32621")

        print("Creating collections in Qdrant...")
        qdrant_client.recreate_collection(
            collection_name="product_images",
            vectors_config=rest.VectorParams(size=512, distance=rest.Distance.COSINE),
        )
        qdrant_client.recreate_collection(
            collection_name="product_titles",
            vectors_config=rest.VectorParams(size=512, distance=rest.Distance.COSINE),
        )
        print("Collections created.")

        for item in data[:100]:  # Limit to the first 100 items
            product, created = Product.objects.get_or_create(
                id=item['id'],
                defaults={
                    'name': item['name'],
                    'description': item.get('description'),
                    'material': item.get('material'),
                    'rating': item.get('rating'),
                    'code': item.get('code'),
                    'brand_id': item.get('brand_id'),
                    'brand_name': item.get('brand_name'),
                    'category_id': item.get('category_id'),
                    'category_name': item.get('category_name'),
                    'gender_id': item.get('gender_id'),
                    'gender_name': item.get('gender_name'),
                    'shop_id': item['shop_id'],
                    'shop_name': item['shop_name'],
                    'link': item.get('link'),
                    'status': item['status'],
                    'colors': item.get('colors', []),
                    'sizes': item.get('sizes', []),
                    'region': item['region'],
                    'currency': item['currency'],
                    'current_price': item['current_price'],
                    'old_price': item.get('old_price'),
                    'off_percent': item.get('off_percent'),
                    'update_date': datetime.fromisoformat(item['update_date']),
                }
            )
            for image_url in item['images']:
                ProductImage.objects.get_or_create(
                    product=product,
                    image_url=image_url
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported the first 100 data entries'))
