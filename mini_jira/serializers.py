from rest_framework import serializers
from .models import Project, Issue, Comment, UserDesignation

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    designation = serializers.CharField(required=False, allow_blank=True)
    avatar_file_id = serializers.IntegerField(required=False)

    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        return value
    def validate_email(self, value):
        if not value.strip():
            raise serializers.ValidationError("Email cannot be empty.")
        return value
    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError("Password cannot be empty.")
        return value
    def validate_designation(self, value):
        if not value:
            return value
        if not value.strip():
            raise serializers.ValidationError("Designation cannot be empty.")
        if not UserDesignation.objects.filter(key=value).exists():
            raise serializers.ValidationError("Invalid designation.")
        return value

    def validate_avatar_file_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("avatar_file_id must be a positive integer.")
        return value


class AttachmentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    attachment_type = serializers.CharField()

    def validate_attachment_type(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("attachment_type is required.")
        return value.strip().lower()

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        return value
    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError("Password cannot be empty.")
        return value

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'description',
            'project',
            'assignee',
            'status',
            'priority',
        ]
        read_only_fields = ['id', 'status']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Issue title cannot be empty.")
        return value
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'issue', 'content']
        read_only_fields = ['id']

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty.")
        return value