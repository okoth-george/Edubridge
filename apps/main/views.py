from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import User
from .Authserializer import UserSerializer, RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ConfirmPasswordSerializer
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from utils.permission import IsStudent, IsSponsor
from rest_framework.decorators import permission_classes
from utils.email import send_email
from django.contrib.auth.hashers import make_password
import random
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your views here.

def generate_jwt(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),       
        "user": UserSerializer(user).data 
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        tokens=generate_jwt(user=validated_data['user'])
        return Response(tokens, status=status.HTTP_200_OK)
        
      
    
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()    
            tokens = generate_jwt(user)           
            return Response(tokens, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():          
            email = serializer.validated_data['email']
            try:
              user = User.objects.get(email=email)
            except User.DoesNotExist:
              return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)   
        
            token=str(random.randint(100000,999999))
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            cache.set(f"reset_token_{email}", token, timeout=600)  # 10 min expiry
            cache.set(f"email_for_token_{token}", email, timeout=600)
           # verification_tokens[email]=tokenhttp://localhost:8080/reset-password/MQ/571900

                 
            try :
                                 
                # Build a frontend link that includes the token and email as query params.
               # reset_link = f"{settings.FRONTEND_URL.rstrip('/')}" \
                   #          f"/reset-password?token={token}&email={email}"
                reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/{uid}/{token}"

                html_message = (
                    f"<p>We received a request to reset your password.</p>"
                    f"<p>Click <a href=\"{reset_link}\">here</a> to open the password reset page.</p>"
                    f"<p>If the link doesn't work, use this token on the reset page: <strong>{token}</strong></p>"
                )

                send_email(
                    subject="Password Reset Request",
                    message=f"Open the link to reset your password: {reset_link}\nOr use token: {token}",
                    recipient_list=[email],
                    html_message=html_message,
                )

                #TODO: Send this token via email (SendGrid, SMTP, etc.)
                print(f"Password reset token for {email}: {token}")

            except Exception as e:
                print(f"Error sending email via Brevo/Anymail: {e}")
                return Response({"error": "Failed to send email verification code "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "Password reset token sent to email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer=ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            #email = serializer.validated_data['email']
            token = serializer.validated_data['token']
            email=cache.get(f"email_for_token_{token}")
            saved_token = cache.get(f"reset_token_{email}")

            if saved_token != token:
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
            
            cache.set(f"verified_email_{email}", True, timeout=600)  # valid for 10 minutes

            return Response({"message": "Token verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ConfirmPasswordSerializer(data=request.data)
        # Accept token either in the request body or as a query param.
        if not serializer.is_valid():
            # Provide more context to the client for debugging
            errors = serializer.errors
            # If token missing, mention how to provide it
            if 'token' in errors and not request.query_params.get('token'):
                errors['token_help'] = 'Provide token in request body (token) or as a query param ?token=...'
            return Response({'errors': errors, 'received': request.data}, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data.get('token') or request.query_params.get('token')
        new_password = serializer.validated_data.get('new_password')

        if not token:
            return Response({"error": "Token not provided. Include in body as 'token' or as query param '?token='"}, status=status.HTTP_400_BAD_REQUEST)

        # Lookup email associated with this token
        email = cache.get(f"email_for_token_{token}")
        if not email:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token matches the stored one
        saved_token = cache.get(f"reset_token_{email}")
        if saved_token != token:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password
        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            # Clear the cached data
            cache.delete(f"reset_token_{email}")
            cache.delete(f"verified_email_{email}")
            cache.delete(f"email_for_token_{token}")

            return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']

            verified = cache.get(f"verified_email_{email}")
            if not verified:
                return Response({"error": "Email not verified for password change"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()

                # Invalidate the verification
                cache.delete(f"verified_email_{email}")

                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
          