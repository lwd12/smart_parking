from django.db import models


# Create your models here.
class Post(models.Model):
    # 생략
    image = models.ImageField(upload_to="images/", null=True, blank=True)

    def __str__(self):
        return str(self.title)
