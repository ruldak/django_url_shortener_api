from django.urls import path
from app.views import RegisterView, LinkListCreateView, LinkDetailView, LinkRedirectView, LinkAnalyticsView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/links/', LinkListCreateView.as_view(), name='link-list-create'),
    path('api/links/<str:short_code>/', LinkDetailView.as_view(), name='link-detail'),
    path('api/links/<str:short_code>/analytics/', LinkAnalyticsView.as_view(), name='link-analytics'),
    path('r/<str:short_code>/', LinkRedirectView.as_view(), name='link-redirect'),
]