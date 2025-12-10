from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions,generics
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Scholarship,Sponsor
from .serializers import ScholarshipSerializer,SponsorProfileSerializer
from utils.permission import IsSponsorOrReadOnly, IsSponsor
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

class ScholarshipListCreateView(APIView):
    """
    Handles:
    1. GET /api/v1/sponsors/ -> Get all scholarships (read-only, anyone can see)
    2. POST /api/v1/sponsors/ -> Create a new scholarship (sponsor-only)
    """
    def get_permissions(self):
        """
        Override to allow GET requests for anyone,
        but require sponsor role for POST requests.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsSponsor()]
        return [permissions.AllowAny()]

    def get(self, request):
        scholarships = Scholarship.objects.all().order_by('-created_at')
        serializer = ScholarshipSerializer(scholarships, many=True)
        return Response(serializer.data)

    def post(self, request):
        # At this point, user is authenticated and is a sponsor (checked by get_permissions)
        serializer = ScholarshipSerializer(data=request.data)
        if serializer.is_valid():
            # Auto-assign the logged-in user as the sponsor
            serializer.save(sponsor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SponsorScholarshipsView(APIView):
    """
    Handles:
    GET /api/v1/sponsors/sponsor/my-scholarships/
    Returns only the scholarships created by the logged-in sponsor.
    Requires sponsor role.
    """
    permission_classes = [permissions.IsAuthenticated, IsSponsor]

    def get(self, request):
        scholarships = Scholarship.objects.filter(sponsor=request.user).order_by('-created_at')
        serializer = ScholarshipSerializer(scholarships, many=True)
        return Response(serializer.data)

class ScholarshipSearchView(APIView):
    """
    Handles:
    GET /api/v1/sponsors/search/?q=...
    """
    def get(self, request):
        query = request.query_params.get('q', '')
        if query:
            results = Scholarship.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(criteria__icontains=query) |
                Q(sponsor__username__icontains=query)
            )
        else:
            results = Scholarship.objects.none()
            
        serializer = ScholarshipSerializer(results, many=True)
        return Response(serializer.data)
    

class ScholarshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAuthenticated]
    
    # Ensure sponsors can only edit their OWN scholarships
    def get_queryset(self):
        try:
            # Check if the logged-in user actually has a sponsor profile
            sponsor_profile = self.request.user.sponsor_profile
            return Scholarship.objects.filter(sponsor=self.request.user)
            # 2. If they do, return ONLY their scholarships
            return Scholarship.objects.filter(sponsor=sponsor_profile)
        
        
            
        except ObjectDoesNotExist: 
            # 3. If the user has no profile, return an empty list
            # This causes a 404 Not Found for the user (instead of a 500 crash)
            return Scholarship.objects.none()
        except AttributeError:
             # This handles cases where the related_name might be different (e.g. user.sponsorprofile)
             return Scholarship.objects.none()
        #return Scholarship.objects.filter(sponsor=self.request.user.sponsor_profile)    

class CreateSponsorProfileView(generics.CreateAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        
        # 1. Safety Check: Ensure user doesn't already have a profile
        if hasattr(user, 'sponsor_profile'):
            raise ValidationError({"detail": "You already have a sponsor profile. Please edit the existing one."})

        # 2. Save the profile and link it to the user from the JWT
        serializer.save(user=user)

class ManageSponsorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SponsorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    # This is the magic part. We override get_object.
    # We don't look for a URL parameter. We look at the User.
    def get_object(self):
        try:
            return self.request.user.sponsor_profile
        except Sponsor.DoesNotExist:
            # If the user has no profile, return 404.
            # The frontend will catch this and show the "Create" form.
            raise Http404