from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Project, ProjectMembership, ProjectRole


User = get_user_model()


# =========================
# AUTH SERVICES
# =========================
class AuthService:
    
    def register_user(self, username, email, password):
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        tokens = self._generate_tokens(user)

        return {
            "user": user,
            "tokens": tokens
        }

    def login_user(self, username, password):
        user = authenticate(username=username, password=password)
        if not user:
            raise ValueError("Invalid credentials")

        tokens = self._generate_tokens(user)

        return {
            "user": user,
            "tokens": tokens
        }

    def _generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


# =========================
# PROJECT SERVICE
# =========================
class ProjectService:

    def create_project(self, actor, **data):
        project = Project.objects.create(**data)

        admin_role = ProjectRole.objects.get(key="Admin")

        ProjectMembership.objects.create(
            user=actor,
            project=project,
            role=admin_role
        )

        return project

    def list_projects(self, actor):
        return Project.objects.filter(
            memberships__user=actor
        ).distinct()