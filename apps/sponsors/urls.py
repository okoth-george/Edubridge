from django.urls import path
from .views import (
    ScholarshipListCreateView,
    ScholarshipDetailView,
    SponsorScholarshipsView,
    ScholarshipSearchView,
    CreateSponsorProfileView,
    ManageSponsorProfileView, 
)

urlpatterns = [
    # 1. List all & Create (Matches frontend: getAllScholarships, createScholarship)
    path('scholarship/', ScholarshipListCreateView.as_view(), name='scholarship-list-create'),

    # 2. Retrieve, Update, Delete (Matches frontend: getScholarshipById, updateScholarship, deleteScholarship)
    path('sponsors/<int:pk>/', ScholarshipDetailView.as_view(), name='scholarship-detail'),

    # 3. Custom: My Scholarships (Matches frontend: getSponsorScholarships)
    path('sponsor/my-scholarships/', SponsorScholarshipsView.as_view(), name='my-scholarships'),

    # 4. Custom: Search (Matches frontend: searchScholarships)
    path('search/', ScholarshipSearchView.as_view(), name='scholarship-search'),
    path('sponsor/scholarships/<int:pk>/', ScholarshipDetailView.as_view(), name='scholarship-detail'),
    path('sponsor/profile/create/', CreateSponsorProfileView.as_view(), name='create-sponsor-profile'),
    path('sponsor/profile/me/', ManageSponsorProfileView.as_view(), name='my-sponsor-profile'),
]