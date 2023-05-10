from django.db import models


# Create your models here.
class Post(models.Model):
    # 생략
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    is_monitor = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pk} - {"Monitor" if self.is_monitor else "Image"}'

    def display(self):
        if self.is_monitor:
            return "Monitor"
        else:
            return self.image.url

