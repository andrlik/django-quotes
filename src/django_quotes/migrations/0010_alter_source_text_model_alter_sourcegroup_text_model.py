# Generated by Django 5.0.4 on 2024-04-05 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_markov", "0005_alter_markovtextmodel_data"),
        ("django_quotes", "0009_alter_source_text_model_alter_sourcegroup_text_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="source",
            name="text_model",
            field=models.OneToOneField(
                blank=True,
                help_text="The text model for this character.",
                on_delete=django.db.models.deletion.CASCADE,
                to="django_markov.markovtextmodel",
            ),
        ),
        migrations.AlterField(
            model_name="sourcegroup",
            name="text_model",
            field=models.OneToOneField(
                blank=True,
                help_text="The markov model for this group.",
                on_delete=django.db.models.deletion.CASCADE,
                to="django_markov.markovtextmodel",
            ),
        ),
    ]