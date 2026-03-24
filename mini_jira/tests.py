from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from mini_jira.models import Attachment, ProjectRole, User

class AuthApiTests(APITestCase):
	def setUp(self):
		self.client = APIClient()

	def test_register_user(self):
		payload = {
			"username": "newuser",
			"email": "newuser@example.com",
			"password": "newpass123"
		}
		response = self.client.post("/api/register/", payload, format="json")
		self.assertEqual(response.status_code, 201)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)

	def test_register_existing_user(self):
		User.objects.create_user(username="existing", email="existing@example.com", password="pass123")
		payload = {
			"username": "existing",
			"email": "existing@example.com",
			"password": "pass123"
		}
		response = self.client.post("/api/register/", payload, format="json")
		self.assertEqual(response.status_code, 400)
		self.assertIn("error", response.data)

	def test_login_user(self):
		User.objects.create_user(username="loginuser", password="loginpass123")
		payload = {
			"username": "loginuser",
			"password": "loginpass123"
		}
		response = self.client.post("/api/login/", payload, format="json")
		self.assertEqual(response.status_code, 200)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)

	def test_login_invalid_credentials(self):
		payload = {
			"username": "nouser",
			"password": "wrongpass"
		}
		response = self.client.post("/api/login/", payload, format="json")
		self.assertEqual(response.status_code, 401)
		self.assertIn("error", response.data)

	def test_register_user_with_uploaded_avatar_file_id(self):
		avatar_path = Path(settings.BASE_DIR) / "avatar.png"

		with avatar_path.open("rb") as avatar_file:
			upload_response = self.client.post(
				"/api/upload-attachment/",
				{"file": avatar_file, "attachment_type": "avatar"},
				format="multipart",
			)

		self.assertEqual(upload_response.status_code, 201)
		self.assertIn("file_id", upload_response.data)

		payload = {
			"username": "avataruser",
			"email": "avataruser@example.com",
			"password": "newpass123",
			"avatar_file_id": upload_response.data["file_id"],
		}
		register_response = self.client.post("/api/register/", payload, format="json")

		self.assertEqual(register_response.status_code, 201)
		user = User.objects.get(username="avataruser")
		self.assertEqual(user.avatar_id, upload_response.data["file_id"])

	def test_upload_avatar_rejects_non_image_file(self):
		non_image_file = SimpleUploadedFile(
			"avatar.txt",
			b"this-is-not-an-image",
			content_type="text/plain",
		)

		response = self.client.post(
			"/api/upload-attachment/",
			{"file": non_image_file, "attachment_type": "avatar"},
			format="multipart",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("error", response.data)
		self.assertEqual(Attachment.objects.filter(attachment_type="avatar").count(), 0)

class ProjectApiTests(APITestCase):
	def setUp(self):
		# Seed ProjectRole lookup table
		ProjectRole.objects.get_or_create(key="Admin", label="Admin")
		ProjectRole.objects.get_or_create(key="Developer", label="Developer")
		ProjectRole.objects.get_or_create(key="Viewer", label="Viewer")
		self.user = User.objects.create_user(username="testuser", password="testpass123")
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)

	def test_get_projects_authenticated(self):
		response = self.client.get("/api/projects/")
		self.assertEqual(response.status_code, 200)
		self.assertIsInstance(response.json(), list)

	def test_create_project_authenticated(self):
		payload = {"name": "Test Project", "description": "A test."}
		response = self.client.post("/api/projects/", payload, format="json")
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["name"], payload["name"])
