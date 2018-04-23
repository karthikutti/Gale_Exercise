import json
from django.db import models


class ScrapyItem(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    url = models.TextField()
    link_url = models.TextField()
    image_urls = models.TextField()

    @property
    def to_dict(self):
        data = {
            'link_url': json.loads(self.link_url),
            'image_urls': json.loads(self.image_urls),
            'url': self.url
        }
        return data

    def __str__(self):
        return self.unique_id