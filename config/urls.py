from django.urls import path
from app.views import RegisterView, Login, RefreshToken, LinkListCreateView, LinkDetailView, LinkRedirectView, LinkAnalyticsView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', Login.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', RefreshToken.as_view(), name='token_refresh'),

    path('api/links/', LinkListCreateView.as_view(), name='link-list-create'),
    path('api/links/<str:short_code>/', LinkDetailView.as_view(), name='link-detail'),
    path('api/links/<str:short_code>/analytics/', LinkAnalyticsView.as_view(), name='link-analytics'),
    path('r/<str:short_code>/', LinkRedirectView.as_view(), name='link-redirect'),
]