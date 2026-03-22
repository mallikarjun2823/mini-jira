from .models import Project, ProjectMembership

class ProjectService:
    def create_project(self, actor, **data):
        project = Project.objects.create(**data)
        ProjectMembership.objects.create(
            user=actor,
            project=project,
            role=ProjectRole.ADMIN
        )
        return project

    def list_projects(self, actor):
        return Project.objects.filter(
        memberships__user=actor
    ).distinct()