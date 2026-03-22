from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from .models import Project, Issue, Comment

def index(request):
	return HttpResponse("Mini JIRA API")
