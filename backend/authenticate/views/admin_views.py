from rest_framework import generics,permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from ..permissions import IsAdmin
from ..serializers.user_list_serializer import UserListSerializer
from ..serializers.user_update_serializer import UserUpdateSerializer

User = get_user_model()

class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserListSerializer
    queryset = User.objects.all().order_by('first_name')


class UserRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'


    def get_queryset(self):
        return User.objects.filter(is_active=True)

