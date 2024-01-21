from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/register/"
        self.users_url = "/api/users/"

        valid_user_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "testpassword",
            "is_staff": True,
        }
        response = self.client.post(self.register_url, valid_user_data, format="json")
        self.admin_user = response.data
        self.admin_token = self.get_access_token()

    def get_access_token(self):
        response = self.client.post(
            "/api/token/",
            {"email": "testuser@example.com", "password": "testpassword"},
            format="json",
        )
        return response.data.get("access_token")

    def test_register_user_valid_data(self):
        valid_user_data = {
            "email": "testuser23@example.com",
            "name": "Test User 23",
            "password": "testpassword",
            "is_staff": True,
        }
        response = self.client.post(self.register_url, valid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("id" in response.data)
        # Add more assertions as needed

    def test_register_user_invalid_email(self):
        invalid_user_data = {
            "email": "invalidemail",
            "name": "Test User",
            "password": "testpassword",
            "is_staff": True,
        }
        response = self.client.post(self.register_url, invalid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in response.data)
        self.assertEqual(response.data["email"][0], "Enter a valid email address.")

    def test_register_user_missing_fields(self):
        missing_fields_data = {
            "name": "Test User",
        }
        response = self.client.post(
            self.register_url, missing_fields_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in response.data)
        self.assertTrue("password" in response.data)

    def test_register_user_existing_email(self):
        existing_user_data = {
            "email": "existinguser@example.com",
            "name": "Existing User",
            "password": "existingpassword",
            "is_staff": True,
        }
        # Create a user with the same email before attempting to register
        self.client.post(self.register_url, existing_user_data, format="json")

        # Attempt to register with the same email
        response = self.client.post(
            self.register_url, existing_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in response.data)
        self.assertEqual(
            str(response.data["email"][0]),
            "custom user with this email already exists.",
        )

    def test_obtain_token(self):
        response = self.client.post(
            "/api/token/",
            {"email": "testuser@example.com", "password": "testpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access_token" in response.data)

    def test_list_users(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetch_user_valid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        # Register a user
        valid_user_data = {
            "email": "fetchuser@example.com",
            "name": "Fetch User",
            "password": "fetchpassword",
            "is_staff": True,
        }
        response_register = self.client.post(
            self.register_url, valid_user_data, format="json"
        )
        self.assertEqual(response_register.status_code, status.HTTP_201_CREATED)

        # Fetch the registered user by ID
        user_id = response_register.data["id"]
        response_fetch = self.client.get(f"{self.users_url}{user_id}/")
        self.assertEqual(response_fetch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_fetch.data["email"], valid_user_data["email"])

    def test_fetch_user_invalid_id(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        # Attempt to fetch a user with an invalid ID
        invalid_user_id = "invalid-id"
        response_fetch = self.client.get(f"{self.users_url}{invalid_user_id}/")
        self.assertEqual(response_fetch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_fetch.data["error"], f"['“{invalid_user_id}” is not a valid UUID.']")
        self.assertTrue("error" in response_fetch.data)
        

    def test_update_user_valid_payload(self):
        # Register a user
        valid_user_data = {
            "email": "updateuser@example.com",
            "name": "Update User",
            "password": "updatepassword",
            "is_staff": True,
        }
        response_register = self.client.post(
            self.register_url, valid_user_data, format="json"
        )
        self.assertEqual(response_register.status_code, status.HTTP_201_CREATED)

        # Fetch the registered user by ID
        user_id = response_register.data["id"]
        update_data = {"name": "Updated Name"}

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        # Update the user with a valid payload
        response_update = self.client.put(
            f"{self.users_url}{user_id}/", update_data, format="json"
        )
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_update.data["updated_user"]["name"], update_data["name"]
        )

    def test_update_user_invalid_payload_existing_email(self):
        # Register two users
        existing_user_data = {
            "email": "existingemail@example.com",
            "name": "Existing User",
            "password": "existingpassword",
            "is_staff": True,
        }
        self.client.post(self.register_url, existing_user_data, format="json")

        new_user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "newpassword",
            "is_staff": True,
        }
        response_register = self.client.post(
            self.register_url, new_user_data, format="json"
        )
        self.assertEqual(response_register.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        # Fetch the registered user by ID
        user_id = response_register.data["id"]

        # Attempt to update the user with an existing email
        update_data = {"email": existing_user_data["email"]}
        response_update = self.client.put(
            f"{self.users_url}{user_id}/", update_data, format="json"
        )
        self.assertEqual(response_update.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in response_update.data)

        self.assertEqual(
            str(response_update.data["email"][0]),
            "custom user with this email already exists.",
        )

    def test_delete_user_valid_uuid(self):
        # Register a user
        valid_user_data = {
            "email": "deleteuser@example.com",
            "name": "Delete User",
            "password": "deletepassword",
            "is_staff": True,
        }
        response_register = self.client.post(
            self.register_url, valid_user_data, format="json"
        )
        self.assertEqual(response_register.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        # Fetch the registered user by ID
        user_id = response_register.data["id"]

        # Delete the user with a valid UUID
        response_delete = self.client.delete(f"{self.users_url}{user_id}/")
        self.assertEqual(response_delete.status_code, status.HTTP_200_OK)



class NonStaffUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/register/"
        self.users_url = "/api/users/"

        # Create a regular user for testing
        self.non_staff_user = User.objects.create(
            email="user@example.com", name="Regular User", is_staff=False
        )
        self.non_staff_token = self.get_access_token(self.non_staff_user)

        # Create an admin user for testing authorization
        self.admin_user = User.objects.create(
            email="admin@example.com",
            name="Admin User",
            password="test123",
            is_staff=True,
        )
        self.admin_token = self.get_access_token(self.admin_user)

    def get_access_token(self, user):
        response = self.client.post(
            "/api/token/",
            {"email": user.email, "password": "test123"},
            format="json",
        )
        return response.data.get("access_token")

    def test_update_user_non_staff_forbidden(self):
        # Authenticate using the non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Attempt to update the non-staff user's profile
        response = self.client.put(
            f"{self.users_url}{self.non_staff_user.id}/",
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_non_staff_forbidden(self):
        # Authenticate using the non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Attempt to delete the non-staff user's profile
        response = self.client.delete(f"{self.users_url}{self.non_staff_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_user_non_staff_forbidden(self):
        # Authenticate using the non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Attempt to fetch the non-staff user's profile
        response = self.client.get(f"{self.users_url}{self.non_staff_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_non_staff_forbidden(self):
        # Authenticate using the non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.non_staff_token}")

        # Attempt to fetch the list of users
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
