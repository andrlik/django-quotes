# Generated by Django 5.0.4 on 2024-04-09 11:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("django_quotes", "0009_alter_source_text_model_alter_sourcegroup_text_model"),
        ("django_quotes", "0010_alter_source_text_model_alter_sourcegroup_text_model"),
        ("django_quotes", "0011_alter_source_text_model_alter_sourcegroup_text_model"),
        ("django_quotes", "0012_remove_sourcemarkovmodel_source_and_more"),
    ]

    dependencies = [
        ("django_markov", "0005_alter_markovtextmodel_data"),
        ("django_quotes", "0008_auto_20240404_1952"),
    ]

    operations = [
        migrations.AlterField(
            model_name="source",
            name="text_model",
            field=models.OneToOneField(
                blank=True,
                help_text="The text model for this character.",
                null=True,
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
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_markov.markovtextmodel",
            ),
        ),
        migrations.RemoveField(
            model_name="sourcemarkovmodel",
            name="source",
        ),
        migrations.DeleteModel(
            name="GroupMarkovModel",
        ),
        migrations.DeleteModel(
            name="SourceMarkovModel",
        ),
    ]
