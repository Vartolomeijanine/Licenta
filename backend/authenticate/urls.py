from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views.admin_views import AdminUserListView, UserRetrieveUpdateDeleteAPIView
from .views.auth_views import UserProfileView
from .views.logout_view import LogoutView
from .views.protected_view import ProtectedView
from .views.register_view import RegisterView, AdminCreateColleagueView
from .views.roles_view import AdminView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('protected/', ProtectedView.as_view(), name='protected_view'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('admin/create-colleague/', AdminCreateColleagueView.as_view(), name='admin_create_colleague'),
    path('admin-only/', AdminView.as_view(), name='admin-only'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:id>/', UserRetrieveUpdateDeleteAPIView.as_view(), name='admin-user-update'),
]