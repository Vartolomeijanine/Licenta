from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "role")

    def get_role(self, obj):
        if obj.is_superuser or obj.is_staff:
            return "admin"
        return "user"
