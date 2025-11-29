from django.contrib.auth import get_user_model
from rest_framework import serializers

from authenticate.validators import validate_email_format, validate_name

User = get_user_model()


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_email_format])
    first_name = serializers.CharField(validators=[validate_name])
    last_name = serializers.CharField(validators=[validate_name])

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        # 🔥 ne asigurăm că username rămâne mereu identic cu email-ul
        instance.username = instance.email

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance
