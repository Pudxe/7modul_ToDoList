from django.contrib.auth import login, logout
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.models import User
from core.serializers import CreateUserSerializer, LoginSerializer, ProfileSerializer, PasswordUpdateSerializer


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer


class LoginView(CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(data=request.data, status=status.HTTP_200_OK)


class ProfileView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(data=request.data, status=status.HTTP_204_NO_CONTENT)


class PasswordUpdateView(UpdateAPIView):
    serializer_class = PasswordUpdateSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user
