from django.core.management.base import BaseCommand
from django.utils import timezone

import random
from datetime import timedelta
import base64

from mini_jira.models import (
    Project,
    ProjectMembership,
    Issue,
    Comment,
    ProjectRole,
    IssueStatus,
    IssuePriority,
    UserDesignation,
    User
)



class Command(BaseCommand):
    help = "Seed database with sample data"

    # tiny 1x1 PNG (white) base64
    AVATAR_PNG_B64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )


    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data for mini_jira...")

        self.seed_lookup_tables()
        self.stdout.write("Seeded lookup tables (roles, statuses, priorities)")

        users = self.create_users()
        self.stdout.write(f"Created/loaded {len(users)} users")

        projects = self.create_projects(users)
        self.stdout.write(f"Created/loaded {len(projects)} projects")

        issues = self.create_issues_and_comments(projects, users)
        self.stdout.write(f"Created {len(issues)} issues with comments")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    def seed_lookup_tables(self):
        # Project Roles
        roles = [
            ("Admin", "ADMIN"),
            ("Developer", "DEVELOPER"),
            ("Viewer", "VIEWER"),
        ]
        for key, label in roles:
            ProjectRole.objects.get_or_create(key=key, defaults={"label": label})

        # Issue Statuses
        statuses = [
            ("Open", "OPEN"),
            ("InProgress", "IN_PROGRESS"),
            ("Resolved", "RESOLVED"),
            ("Closed", "CLOSED"),
        ]
        for key, label in statuses:
            IssueStatus.objects.get_or_create(key=key, defaults={"label": label})

        # Issue Priorities
        priorities = [
            ("Low", "LOW"),
            ("Medium", "MEDIUM"),
            ("High", "HIGH"),
            ("Critical", "CRITICAL"),
        ]
        for key, label in priorities:
            IssuePriority.objects.get_or_create(key=key, defaults={"label": label})

        # User Designations
        designations = [
            ("Engineer", "ENGINEER"),
            ("Manager", "MANAGER"),
            ("Designer", "DESIGNER"),
            ("QA", "QA"),
        ]
        for key, label in designations:
            UserDesignation.objects.get_or_create(key=key, defaults={"label": label})

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

            # randomly assign avatar to some base users
            if random.random() < 0.5:
                try:
                    user.avatar = base64.b64decode(self.AVATAR_PNG_B64)
                    user.save()
                except Exception:
                    pass

            users.append(user)

        # Add some randomly generated users
        first_names = ["Alex","Sam","Taylor","Jordan","Morgan","Casey","Riley","Avery","Quinn","Rowan"]
        last_names = ["Lee","Patel","Kim","Singh","Lopez","Nguyen","Garcia","Brown","White","Clark"]

        # create 10 random users
        for _ in range(10):
            username = f"user{random.randint(1000,9999)}"
            # ensure uniqueness
            while User.objects.filter(username=username).exists():
                username = f"user{random.randint(1000,9999)}"

            first = random.choice(first_names)
            last = random.choice(last_names)
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                first_name=first,
                last_name=last,
                email=email,
                password="password123",
            )

            # assign a random designation if available
            try:
                desig = random.choice(list(UserDesignation.objects.all()))
                user.designation = desig
                user.save()
            except IndexError:
                pass

            users.append(user)

        # assign avatars to randomly generated users as well (70% chance)
        for u in users:
            if not u.avatar and random.random() < 0.7:
                try:
                    u.avatar = base64.b64decode(self.AVATAR_PNG_B64)
                    u.save()
                except Exception:
                    pass

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

            admin_role = ProjectRole.objects.get(key="Admin")
            dev_role = ProjectRole.objects.get(key="Developer")
            for user in members:
                role = admin_role if user == admin else dev_role
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

                status_obj = random.choice(list(IssueStatus.objects.all()))
                priority_obj = random.choice(list(IssuePriority.objects.all()))
                issue = Issue.objects.create(
                    title=random.choice(titles),
                    description=self.random_text(3),
                    project=project,
                    created_by=created_by,
                    assignee=assignee,
                    status=status_obj,
                    priority=priority_obj,
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
