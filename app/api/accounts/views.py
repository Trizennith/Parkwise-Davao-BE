from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "login"]:
            return [permissions.AllowAny()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            serializer = self.get_serializer(user)
            return Response(
                {"user": serializer.data, "token": str(refresh.access_token)}
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def my_profile(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        serializer.save()


class UserLoginView(TokenObtainPairView):
    """View for user login."""

    permission_classes = (permissions.AllowAny,)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile."""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """View for changing user password."""

    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password successfully updated."}, status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """View for listing all users (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting a specific user (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)
