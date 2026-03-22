from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import ProjectSerializer
from .services import ProjectService


class ProjectListCreateView(APIView):
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        service = ProjectService()
        projects = service.list_projects(actor = request.user)

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ProjectService()
        project = service.create_project(
            actor=request.user,
            **serializer.validated_data
        )

        response_serializer = ProjectSerializer(project)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)