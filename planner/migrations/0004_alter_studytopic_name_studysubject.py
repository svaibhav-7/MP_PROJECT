# Generated by Django 5.0.8 on 2025-03-11 05:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0003_remove_studytopic_difficulty_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='studytopic',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='StudySubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=10)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.studytopic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
