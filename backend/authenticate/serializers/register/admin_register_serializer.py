from .register_serializer import RegisterSerializer
from django.contrib.auth.models import Group

class AdminColleagueCreateSerializer(RegisterSerializer):
    class Meta(RegisterSerializer.Meta):
        pass

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = super().create(validated_data)

        colleague_group, created = Group.objects.get_or_create(name='colleague')
        user.groups.add(colleague_group)
        user.save()

        return user