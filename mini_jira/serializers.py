from rest_framework import serializers
from .models import Project, Issue, Comment

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