from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name='register'),
	path('login/', views.LoginView.as_view(), name='login'),
	path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
	path('upload-attachment/', views.AttachmentUploadView.as_view(), name='upload-attachment'),
]
