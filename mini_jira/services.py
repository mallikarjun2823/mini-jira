import imghdr

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Attachment, Project, ProjectMembership, ProjectRole, User, UserDesignation
# =========================
# AUTH SERVICES
# =========================
class AuthService:
    
    def register_user(self, username, email, password, designation=None, avatar_file_id=None):
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")

        avatar_attachment = None
        if avatar_file_id is not None:
            avatar_attachment = Attachment.objects.filter(id=avatar_file_id).first()
            if not avatar_attachment:
                raise ValueError("Invalid avatar_file_id")
            if avatar_attachment.attachment_type != "avatar":
                raise ValueError("Attachment is not an avatar")
            if User.objects.filter(avatar=avatar_attachment).exists():
                raise ValueError("Avatar attachment is already used")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            designation=designation,
        )

        if avatar_attachment:
            user.avatar = avatar_attachment
            avatar_attachment.uploaded_by = user
            avatar_attachment.save(update_fields=["uploaded_by"])
            user.save(update_fields=["avatar"])

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

class AttachmentService:

    def upload_attachment(self, actor, file, attachment_type):
        if not file:
            raise ValueError("file is required")
        if not attachment_type:
            raise ValueError("attachment_type is required")

        normalized_type = attachment_type.lower().strip()
        if normalized_type == "avatar":
            file.seek(0)
            image_kind = imghdr.what(file)
            file.seek(0)
            if image_kind is None:
                raise ValueError("Invalid file type for avatar. Only image files are allowed.")

        attachment = Attachment.objects.create(
            file=file,
            attachment_type=normalized_type,
            uploaded_by=actor
        )
        return attachment