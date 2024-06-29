from django.shortcuts import render
from .models import Product
from .forms import SearchForm
from qdrant_client import QdrantClient
from transformers import CLIPProcessor, CLIPModel
import torch
import requests
# import openai

# openai.api_key = 'pk-EvyWAcEPWAmoRDdirVkPKoWwwndXtIXcruVHESuftpxvELYy'
# openai.base_url = "https://api.pawan.krd/v1/"

# Initialize Qdrant client
qdrant_client = QdrantClient(url="efd9ea28-a235-417e-b78f-cb7eeef3e56a.hsvc.ir:32621")

# Load the CLIP model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("models/clip-vit-base-patch32", local_files_only=True).to(device)
clip_processor = CLIPProcessor.from_pretrained("models/clip-vit-base-patch32", local_files_only=True)

def encode_text(text):
    inputs = clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        text_features = clip_model.get_text_features(**inputs)
    return text_features.cpu().numpy()

def apply_filters(products, filters):
    if filters.get('min_price'):
        products = products.filter(current_price__gte=filters['min_price'])
    if filters.get('max_price'):
        products = products.filter(current_price__lte=filters['max_price'])
    if filters.get('category'):
        products = products.filter(category_name__icontains=filters['category'])
    if filters.get('brand'):
        products = products.filter(brand_name__icontains=filters['brand'])
    if filters.get('in_stock'):
        products = products.filter(status='IN_STOCK')
    return products

# def get_search_weights(query):
#     completion = openai.chat.completions.create(
#         model="pai-001",
#         messages=[
#             {"role": "user", "content": f"User query: '{query}'\nHow much importance should be given to semantic image search and how much to keyword search? Provide the percentages in the format: 'image_search: X%, keyword_search: Y%'."},
#         ],
#     )
#     result = completion.choices[0].message.content
#     print(f"Model response: {result}")
    
#     image_search_weight = 0.5  # Default
#     keyword_search_weight = 0.5  # Default
#     try:
#         parts = result.split(',')
#         for part in parts:
#             if 'image_search' in part:
#                 image_search_weight = float(part.split(':')[1].strip().replace('%', '')) / 100
#             elif 'keyword_search' in part:
#                 keyword_search_weight = float(part.split(':')[1].strip().replace('%', '')) / 100
#     except Exception as e:
#         print(f"Error parsing model response: {e}")

#     return image_search_weight, keyword_search_weight

def search(request):
    query = None
    results = []
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            filters = {
                'min_price': form.cleaned_data.get('min_price'),
                'max_price': form.cleaned_data.get('max_price'),
                'category': form.cleaned_data.get('category'),
                'brand': form.cleaned_data.get('brand'),
                'in_stock': form.cleaned_data.get('in_stock'),
            }

            query_vector = encode_text(query)[0]

            # Get weights from OpenAI
            # image_weight, text_weight = get_search_weights(query)

            # Perform search in Qdrant for product names
            name_search_result = qdrant_client.search(
                collection_name="product_titles",
                query_vector=query_vector,
                limit=5
            )

            # Perform search in Qdrant for product images
            image_search_result = qdrant_client.search(
                collection_name="product_images",
                query_vector=query_vector,
                limit=5
            )

            # Combine results from both searches
            product_ids = {result.payload['product_id'] for result in name_search_result + image_search_result}
            products = Product.objects.filter(id__in=product_ids).prefetch_related('images')

            # Apply filters
            results = apply_filters(products, filters)
    else:
        form = SearchForm()
    return render(request, 'searchapp/search.html', {'form': form, 'query': query, 'results': results})