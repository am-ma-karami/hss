# Generated by Django 4.2.6 on 2024-06-28 18:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('material', models.CharField(blank=True, max_length=255, null=True)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('code', models.CharField(blank=True, max_length=100, null=True)),
                ('brand_id', models.IntegerField(blank=True, null=True)),
                ('brand_name', models.CharField(blank=True, max_length=255, null=True)),
                ('category_id', models.IntegerField(blank=True, null=True)),
                ('category_name', models.CharField(blank=True, max_length=255, null=True)),
                ('gender_id', models.IntegerField(blank=True, null=True)),
                ('gender_name', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_id', models.IntegerField()),
                ('shop_name', models.CharField(max_length=255)),
                ('link', models.URLField(blank=True, max_length=500, null=True)),
                ('status', models.CharField(max_length=50)),
                ('colors', models.JSONField(blank=True, null=True)),
                ('sizes', models.JSONField(blank=True, null=True)),
                ('region', models.CharField(max_length=100)),
                ('currency', models.CharField(max_length=10)),
                ('current_price', models.FloatField()),
                ('old_price', models.FloatField(blank=True, null=True)),
                ('off_percent', models.FloatField(blank=True, null=True)),
                ('update_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('image_embedding', models.BinaryField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='searchapp.product')),
            ],
        ),
    ]
