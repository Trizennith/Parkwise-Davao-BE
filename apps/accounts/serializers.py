from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Use the default password hasher
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'role' in validated_data:
            if validated_data['role'] == 'admin':
                instance.is_staff = True
            else:
                instance.is_staff = False
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # Hash the password
            validated_data.pop('password')
        return super().update(instance, validated_data)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name', 
                 'role', 'status', 'avatar_url', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'write_only': True}
        }

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 
                 'first_name', 'last_name', 'role')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user data."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar_url')
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'status', 'avatar_url', 'phone_number')
        read_only_fields = ('id',) 