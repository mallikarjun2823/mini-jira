from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

import random
from datetime import timedelta

from mini_jira.models import (
    Project,
    ProjectMembership,
    Issue,
    Comment,
    ProjectRole,
    IssueStatus,
    IssuePriority,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data for mini_jira...")

        users = self.create_users()
        self.stdout.write(f"Created/loaded {len(users)} users")

        projects = self.create_projects(users)
        self.stdout.write(f"Created/loaded {len(projects)} projects")

        issues = self.create_issues_and_comments(projects, users)
        self.stdout.write(f"Created {len(issues)} issues with comments")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    # =========================
    # Users
    # =========================
    def create_users(self):
        base_users = [
            ("alice", "Alice", "Anderson"),
            ("bob", "Bob", "Brown"),
            ("carol", "Carol", "Clark"),
            ("dave", "Dave", "Dawson"),
            ("eve", "Eve", "Evans"),
            ("frank", "Frank", "Fisher"),
            ("grace", "Grace", "Green"),
            ("heidi", "Heidi", "Hansen"),
            ("ivan", "Ivan", "Iverson"),
            ("judy", "Judy", "Jones"),
        ]

        users = []
        for username, first, last in base_users:
            email = f"{username}@example.com"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                },
            )

            if created:
                user.set_password("password123")
                user.save()

            users.append(user)

        return users

    # =========================
    # Projects + Memberships
    # =========================
    def create_projects(self, users):
        names = [
            ("Apollo", "Landing payments and billing"),
            ("Hermes", "Notifications and messaging"),
            ("Zephyr", "Realtime analytics pipeline"),
            ("Orion", "User management and auth"),
            ("Atlas", "Maps and geolocation"),
            ("Nimbus", "File storage service"),
            ("Pioneer", "Onboarding flow"),
            ("Catalyst", "Marketing automation"),
            ("Vertex", "3D rendering engine"),
            ("Summit", "Reporting and dashboards"),
        ]

        projects = []

        for name, desc in names:
            project, _ = Project.objects.get_or_create(
                name=name,
                defaults={"description": desc},
            )

            # assign members (3–5 users)
            member_count = random.randint(3, 5)
            members = random.sample(users, k=member_count)

            admin = random.choice(members)

            for user in members:
                role = ProjectRole.ADMIN if user == admin else ProjectRole.DEVELOPER

                ProjectMembership.objects.get_or_create(
                    user=user,
                    project=project,
                    defaults={"role": role},
                )

            projects.append(project)

        return projects

    # =========================
    # Helper
    # =========================
    def random_text(self, sentences=2):
        sample_phrases = [
            "Implement the core flow for the feature.",
            "Fix edge cases and improve validation.",
            "Refactor to use service layer and serializers.",
            "Add unit tests and integration tests.",
            "Improve error handling and logging.",
            "Optimize performance for large datasets.",
            "Design API contract and document endpoints.",
            "Address security and permission checks.",
            "Migrate legacy data to the new format.",
            "Polish UI and improve accessibility.",
        ]

        return " ".join(random.choice(sample_phrases) for _ in range(sentences))

    # =========================
    # Issues + Comments
    # =========================
    def create_issues_and_comments(self, projects, users):
        titles = [
            "Cannot save user profile",
            "Error when uploading files",
            "Slow response on reports page",
            "Notification emails not sent",
            "Permission denied for admin actions",
            "Unexpected 500 on checkout",
            "Search returns incomplete results",
            "Timezone parsing issue",
            "CSV export fails for large files",
            "Mobile layout broken on iOS",
        ]

        created_issues = []

        for project in projects:
            issue_count = random.randint(3, 7)

            members = [m.user for m in project.memberships.all()] or users

            for _ in range(issue_count):
                created_by = random.choice(members)
                assignee = random.choice(members + [None])

                created_at = timezone.now() - timedelta(days=random.randint(0, 90))

                issue = Issue.objects.create(
                    title=random.choice(titles),
                    description=self.random_text(3),
                    project=project,
                    created_by=created_by,
                    assignee=assignee,
                    status=random.choice(list(IssueStatus.values)),
                    priority=random.choice(list(IssuePriority.values)),
                    created_at=created_at,
                    updated_at=created_at + timedelta(hours=random.randint(0, 72)),
                )

                # comments
                for _ in range(random.randint(1, 4)):
                    commenter = random.choice(users)
                    comment_time = issue.created_at + timedelta(hours=random.randint(1, 120))

                    Comment.objects.create(
                        issue=issue,
                        created_by=commenter,
                        content=self.random_text(1),
                        created_at=comment_time,
                        updated_at=comment_time,
                    )

                created_issues.append(issue)

        return created_issues
