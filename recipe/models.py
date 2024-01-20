from django.db import models
from users.models import CustomUser

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    ingredients = models.TextField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title