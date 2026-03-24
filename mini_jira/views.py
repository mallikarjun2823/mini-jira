from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import AttachmentUploadSerializer, ProjectSerializer, UserRegistrationSerializer, UserLoginSerializer
from .services import AttachmentService, AuthService, ProjectService

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthService()

        try:
            username = serializer.validated_data["username"]
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            designation = serializer.validated_data.get("designation")
            avatar_file_id = serializer.validated_data.get("avatar_file_id")
            result = service.register_user(
                username=username,
                email=email,
                password=password,
                designation=designation,
                avatar_file_id=avatar_file_id,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "access": result["tokens"]["access"],
            "refresh": result["tokens"]["refresh"]
        }, status=status.HTTP_201_CREATED)
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthService()

        try:
            username,password = serializer.validated_data["username"],serializer.validated_data["password"]
            result = service.login_user(username=username, password=password)
        except ValueError as e:
            return Response({"error": str(e)}, status=401)

        return Response({
            "access": result["tokens"]["access"],
            "refresh": result["tokens"]["refresh"]
        }, status=status.HTTP_200_OK)

        
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

class AttachmentUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        attachment_type = serializer.validated_data["attachment_type"]

        service = AttachmentService()
        try:
            actor = request.user if request.user.is_authenticated else None
            response = service.upload_attachment(
                actor=actor,
                file=file,
                attachment_type=attachment_type
            )
            return Response({"message": "Attachment uploaded successfully", "file_id": response.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
