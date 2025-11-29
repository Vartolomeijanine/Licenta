# cases/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from compensation.models import Complaint
from .enum import StatusChoices

User = get_user_model()

class AssignComplaintSerializer(serializers.ModelSerializer):
    assigned_colleague = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )

    class Meta:
        model = Complaint
        fields = ["id", "assigned_colleague", "status"]
        read_only_fields = ["status"]

    def update(self, instance, validated_data):
        instance.assigned_colleague = validated_data["assigned_colleague"]
        instance.status = StatusChoices.UNDER_VERIFICATION.value
        instance.save()
        return instance
