# Generated by Django 2.0.4 on 2018-04-15 17:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scrapyitem',
            old_name='data',
            new_name='img_urls',
        ),
        migrations.AddField(
            model_name='scrapyitem',
            name='link_url',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
