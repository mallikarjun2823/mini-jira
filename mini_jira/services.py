from .models import Project, ProjectMembership,ProjectRole

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