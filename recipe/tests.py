from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser
from .models import Recipe


class RecipeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recipes_url = "/api/recipes/"
        # Create a staff user for testing
        self.user = CustomUser.objects.create_user(
            email="admin@example.com", name="Admin Admin", password="testpassword", is_staff=True
        )
        self.token = self.get_access_token(self.user)

        # Create a non staff user for testing authorization
        self.non_staff_user = CustomUser.objects.create_user(
            email="nonstaff@example.com", name="Non Staff", password="testpassword", is_staff=False
        )
        self.non_staff_token = self.get_access_token(self.non_staff_user)

        # Create a recipe
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            instructions="Test instructions",
            ingredients="Test ingredients",
            owner=self.user,
        )

        # Create a recipe where a non staff is the owner
        self.recipe_non_staff = Recipe.objects.create(
            title="Test Recipe",
            instructions="Test instructions",
            ingredients="Test ingredients",
            owner=self.non_staff_user,
        )

    def get_access_token(self, user):
        response = self.client.post(
            "/api/token/",
            {"email": user.email, "password": "testpassword"},
            format="json",
        )
        return response.data.get("access_token")

    def test_list_recipes(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_recipe(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "title": "New Recipe",
            "instructions": "New instructions",
            "ingredients": "New ingredients",
        }
        response = self.client.post("/api/recipes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_recipe(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(f"/api/recipes/{self.recipe.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Recipe")

    def test_update_recipe(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "title": "Updated Recipe",
            "instructions": "Updated instructions",
            "ingredients": "Updated ingredients",
        }
        response = self.client.put(
            f"/api/recipes/{self.recipe.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_recipe"]["title"], "Updated Recipe")
        self.assertEqual(
            response.data["updated_recipe"]["instructions"], "Updated instructions"
        )
        self.assertEqual(
            response.data["updated_recipe"]["ingredients"], "Updated ingredients"
        )

    def test_delete_recipe(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.delete(f"/api/recipes/{self.recipe.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_recipe_missing_title(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "instructions": "Updated instructions",
            "ingredients": "Updated ingredients",
        }
        response = self.client.put(
            f"/api/recipes/{self.recipe.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("title" in response.data)

    def test_update_recipe_missing_instructions(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "title": "Updated Recipe",
            "ingredients": "Updated ingredients",
        }
        response = self.client.put(
            f"/api/recipes/{self.recipe.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("instructions" in response.data)

    def test_update_recipe_missing_ingredients(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "title": "Updated Recipe",
            "instructions": "Updated instructions",
        }
        response = self.client.put(
            f"/api/recipes/{self.recipe.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("ingredients" in response.data)

    def test_create_recipe_missing_title(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "instructions": "Recipe instructions",
            "ingredients": "Recipe ingredients",
        }
        response = self.client.post("/api/recipes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("title" in response.data)

    def test_create_recipe_missing_instructions(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "title": "New Recipe",
            "ingredients": "Recipe ingredients",
        }
        response = self.client.post("/api/recipes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("instructions" in response.data)

    def test_create_recipe_missing_ingredients(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {
            "title": "New Recipe",
            "instructions": "Recipe instructions",
        }
        response = self.client.post("/api/recipes/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("ingredients" in response.data)

    def test_fetch_recipe(self):
        # Authenticate as a non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Fetch the recipe
        response = self.client.get(f"{self.recipes_url}{self.recipe.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_recipe_as_owner(self):
        # Authenticate as the owner of the recipe
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Update the recipe
        data = {
            "title": "Updated Recipe",
            "instructions": "Updated instructions",
            "ingredients": "Updated ingredients",
        }
        response = self.client.put(f"{self.recipes_url}{self.recipe_non_staff.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_recipe"]["title"], "Updated Recipe")

    def test_update_recipe_as_staff(self):
        # Authenticate as a staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Update the recipe
        data = {
            "title": "Updated Recipe",
            "instructions": "Updated instructions",
            "ingredients": "Updated ingredients",
        }
        response = self.client.put(f"{self.recipes_url}{self.recipe.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["updated_recipe"]["title"], "Updated Recipe")

    def test_update_recipe_as_non_owner_non_staff(self):
        # Authenticate as a non-owner non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Attempt to update the recipe (should fail)
        data = {
            "title": "Updated Recipe",
            "instructions": "Updated instructions",
            "ingredients": "Updated ingredients",
        }
        response = self.client.put(f"{self.recipes_url}{self.recipe.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_recipe_as_owner(self):
        # Authenticate as the owner of the recipe
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Delete the recipe
        response = self.client.delete(f"{self.recipes_url}{self.recipe_non_staff.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_recipe_as_staff(self):
        # Authenticate as a staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Delete the recipe
        response = self.client.delete(f"{self.recipes_url}{self.recipe.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_recipe_as_non_owner_non_staff(self):
        # Authenticate as a non-owner non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Attempt to delete the recipe (should fail)
        response = self.client.delete(f"{self.recipes_url}{self.recipe.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)