from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# =========================
# Lookup Tables
# =========================
class UserDesignation(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label

class ProjectRole(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class IssueStatus(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class IssuePriority(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label

class User(AbstractUser):
    avatar = models.BinaryField(blank=True, null=True)
    designation = models.ForeignKey(
        UserDesignation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
# =========================
# Project
# =========================
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectMembership",
        related_name="projects"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# =========================
# Project Membership (RBAC Core)
# =========================
class ProjectMembership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.ForeignKey(
        ProjectRole,
        on_delete=models.PROTECT,
        related_name="memberships"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} -> {self.project.name} ({self.role})"


# =========================
# Issue
# =========================
class Issue(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_issues"
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues"
    )

    status = models.ForeignKey(
        IssueStatus,
        on_delete=models.PROTECT,
        related_name="issues"
    )

    priority = models.ForeignKey(
        IssuePriority,
        on_delete=models.PROTECT,
        related_name="issues"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# =========================
# Comment
# =========================
class Comment(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.created_by.username} on {self.issue.title}"