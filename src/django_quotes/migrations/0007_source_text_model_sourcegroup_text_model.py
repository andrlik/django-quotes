# Generated by Django 5.0.4 on 2024-04-04 19:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_markov", "0005_alter_markovtextmodel_data"),
        ("django_quotes", "0006_alter_source_description_rendered"),
    ]

    operations = [
        migrations.AddField(
            model_name="source",
            name="text_model",
            field=models.OneToOneField(
                help_text="The text model for this character.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_markov.markovtextmodel",
            ),
        ),
        migrations.AddField(
            model_name="sourcegroup",
            name="text_model",
            field=models.OneToOneField(
                help_text="The markov model for this group.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_markov.markovtextmodel",
            ),
        ),
    ]
