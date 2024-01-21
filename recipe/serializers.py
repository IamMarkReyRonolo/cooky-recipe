from rest_framework import serializers
from .models import Recipe
from django.core.validators import URLValidator, MinValueValidator, RegexValidator

class RecipeSerializer(serializers.ModelSerializer):
    number_of_servings = serializers.IntegerField(default=1, validators=[MinValueValidator(1)])
    main_image = serializers.URLField(default="https://picsum.photos/seed/picsum/200/300", validators=[URLValidator()])
    preparation_time = serializers.CharField(
        default="00:10:10",
        validators=[
            RegexValidator(
                regex=r'^\d+:\d+:\d+$',
                message='Preparation time must be in the format HH:MM:SS.',
                code='invalid_preparation_time'
            )
        ]
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {'owner': {'read_only': True}}

    def create(self, validated_data):
        # Get the current user from the request
        user = self.context['request'].user

        # Add the user as the owner when creating a new Recipe
        validated_data['owner'] = user

        # Call the default create method to save the instance
        return super().create(validated_data)