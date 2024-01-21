from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Recipe
from .serializers import RecipeSerializer
from .permissions import IsAdminOrReadOnly, IsRecipeOwnerOrAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(method="POST", request_body=RecipeSerializer)
@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def recipe_list(request):
    if request.method == "GET":
        if request.user.is_staff:
            # If user is staff, fetch all recipes
            recipes = Recipe.objects.all()
        else:
            # If user is not staff, fetch only their own recipes
            recipes = Recipe.objects.filter(owner=request.user)

        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = RecipeSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="PUT", request_body=RecipeSerializer)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([permissions.IsAuthenticated, IsRecipeOwnerOrAdmin])
def recipe_detail(request, pk):
    try:
        recipe = Recipe.objects.get(pk=pk)
    except Recipe.DoesNotExist:
        return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    elif request.method == "PUT":
        # Check if the user is a staff member or the owner of the recipe
        if not request.user.is_staff and request.user != recipe.owner:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = RecipeSerializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Successfully updated", "updated_recipe": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        # Check if the user is a staff member or the owner of the recipe
        if not request.user.is_staff and request.user != recipe.owner:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        recipe.delete()
        return Response({"message": "Successfully deleted"}, status=status.HTTP_200_OK)
