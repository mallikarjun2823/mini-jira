from django.db import models
from django.contrib.auth.models import User


# =========================
# Enums / Choices
# =========================
class ProjectRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    DEVELOPER = "developer", "Developer"
    VIEWER = "viewer", "Viewer"


class IssueStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class IssuePriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


# =========================
# Project
# =========================
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    members = models.ManyToManyField(
        User,
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
        User,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(max_length=20, choices=ProjectRole.choices)

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
        User,
        on_delete=models.CASCADE,
        related_name="created_issues"
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues"
    )

    status = models.CharField(
        max_length=20,
        choices=IssueStatus.choices,
        default=IssueStatus.OPEN
    )

    priority = models.CharField(
        max_length=20,
        choices=IssuePriority.choices,
        default=IssuePriority.MEDIUM
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
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.created_by.username} on {self.issue.title}"