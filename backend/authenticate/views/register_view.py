from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..permissions import IsAdmin
from ..serializers.register.admin_register_serializer import AdminColleagueCreateSerializer
from ..serializers.register.register_serializer import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        user.last_login = timezone.now()
        user.save()

        token_serializer = TokenObtainPairSerializer(data={
            'username': user.email,
            'password': request.data['password']
        })

        token_serializer.is_valid(raise_exception=True)

        response_data = {
            'user': serializer.data,
            'tokens': token_serializer.validated_data
        }

        headers = self.get_success_headers(serializer.data)

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class AdminCreateColleagueView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminColleagueCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": f"Colleague user {user.email} created successfully.",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": "colleague"
            }
        }, status=status.HTTP_201_CREATED)