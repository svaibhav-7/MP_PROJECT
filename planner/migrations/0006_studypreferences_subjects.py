# Generated by Django 5.1.2 on 2025-04-09 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0005_alter_studytopic_name_delete_studysubject'),
    ]

    operations = [
        migrations.AddField(
            model_name='studypreferences',
            name='subjects',
            field=models.TextField(default='[]'),
        ),
    ]
