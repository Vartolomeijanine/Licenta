"""
URL configuration for color_analysis_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from authenticate.views.login_view import LoginView

@api_view(['POST'])
@permission_classes([AllowAny])
def session_login(request):
    """Login cu sesiune Django (funcționează din browser)"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'detail': 'Email and password required'}, status=400)
    
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=401)
    
    login(request, user)
    return Response({'message': f'Logat ca {email}'}, status=200)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("authenticate.urls")),

    # login cu email
    path("api/token/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/login/", session_login, name="session_login"),
    path("api/coloranalysis/", include("coloranalysis.urls")),
    
    # Upload page
    path("upload/", TemplateView.as_view(template_name='upload.html'), name='upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


