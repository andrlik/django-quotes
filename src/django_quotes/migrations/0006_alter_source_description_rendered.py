# Generated by Django 5.0.4 on 2024-04-03 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_quotes", "0001_squashed_0005_alter_groupmarkovmodel_created_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="source",
            name="description_rendered",
            field=models.TextField(
                blank=True, help_text="Automatically generated from description on save.", null=True
            ),
        ),
    ]
