from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role','password']
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only':True} # Ensures password is never returned
        }
class LoginSerializer(serializers.Serializer):
    """
    Serializer to handle user login, authentication, and JWT generation.
    """
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    
    # Fields that will be returned upon successful login
    token = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        request = self.context.get('request')

        if email and password:
            # 1. Authenticate the user against credentials
            user = authenticate(request=request, username=email, password=password)

            if not user:
                # Authentication failed
                msg = _('Invalid email or password.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        # 2. Generate Tokens upon successful authentication
        refresh = RefreshToken.for_user(user)
        
        # 3. Store data for the view's response
        data['user'] = user
        data['refresh'] = str(refresh)
        data['token'] = str(refresh.access_token)
        
        return data

    def get_user_data(self, data):
        """
        Custom method to return essential user data for the frontend.
        Note: The user object is accessed via data['user'] after successful validation.
        """
        # We need to manually serialize the user object here.      
        user = data.get('user')

        if user:
            return UserSerializer(user).data
         
        return None



class LogiinSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(label=_('password'),write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")
        


        # Authenticate user
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "username": user.username,
            }
        }
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'role']

    def create(self, data):
        user = User.objects.create_user(
            name=data['name'],
            email= data['email'],
            password= data['password'],
            role= data['role']
        )
        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"), write_only=True)
   
    
class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=6)   

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value 

    def validate_new_password(self, value):
        # Add any password strength validation here if needed
        return value
class ConfirmPasswordSerializer(serializers.Serializer):
    pass
       