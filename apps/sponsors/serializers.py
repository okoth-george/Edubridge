
from rest_framework import serializers
from django.utils import timezone
from .models import Scholarship
from apps.sponsors.models import Sponsor

class ScholarshipSerializer(serializers.ModelSerializer):
    # Display the username of the sponsor (Read-Only)
    sponsor_name = serializers.ReadOnlyField(source='sponsor.username')
    
    # Calculated field for days left
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Scholarship
        fields = [
            'id',
            'sponsor',        # The ID (hidden/read-only in this context)
            'sponsor_name',   # The readable name for frontend
            'title',
            'description',
            'criteria',
            'amount',
            'deadline',
            'is_active',
            'created_at',
            'days_remaining',
        ]
        read_only_fields = ['sponsor', 'created_at', 'days_remaining']

    def get_days_remaining(self, obj):
        if not obj.deadline:
            return None
        today = timezone.now().date()
        delta = obj.deadline - today
        if delta.days < 0:
            return "Expired"
        return f"{delta.days} days"

    def validate_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("The deadline cannot be in the past.")
        return value
    
class SponsorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        # Include all sponsor profile fields except 'user' (OneToOneField to User)
        fields = [
            'id',
            'organization_name',
            'contact_number',
            'website',
            'email',
            'name',
            'description'
        ]
        read_only_fields = ['id']    