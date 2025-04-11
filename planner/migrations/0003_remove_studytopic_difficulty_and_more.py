# Generated by Django 5.1.2 on 2025-03-03 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_studypreferences_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studytopic',
            name='difficulty',
        ),
        migrations.RemoveField(
            model_name='studytopic',
            name='importance',
        ),
        migrations.RemoveField(
            model_name='studytopic',
            name='min_time',
        ),
        migrations.AddField(
            model_name='studytopic',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='studytopic',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
