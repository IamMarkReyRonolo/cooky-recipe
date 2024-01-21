from django.db import models
from users.models import CustomUser
import uuid
from django.core.validators import URLValidator, MinValueValidator, RegexValidator

class Recipe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    number_of_servings = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    main_image = models.URLField(
        validators=[URLValidator()]
    )
    preparation_time = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^\d+:\d+:\d+$',
                message='Preparation time must be in the format HH:MM:SS.',
                code='invalid_preparation_time'
            )
        ]
    )
    instructions = models.TextField()
    ingredients = models.TextField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title