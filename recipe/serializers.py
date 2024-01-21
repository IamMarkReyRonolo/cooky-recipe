from rest_framework import serializers
from .models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
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