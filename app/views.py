from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from datetime import timedelta
from .models import Link, LinkClick
from .serializers import LinkSerializer, LinkAnalyticsSerializer, RegisterSerializer
from .utils import anonymize_ip, parse_user_agent, get_client_ip, get_country_from_ip
from .permissions import IsOwnerOrReadOnly, CanEditLink
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LinkListCreateView(generics.ListCreateAPIView):
    """
    View untuk membuat dan melihat daftar link
    """
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Hanya tampilkan link aktif yang belum expired
        queryset = Link.objects.filter(is_active=True)
        
        # Filter untuk user yang terautentikasi
        if self.request.user.is_authenticated:
            return queryset.filter(created_by=self.request.user)
        
        # Untuk anonymous user, hanya tampilkan link tanpa created_by
        return queryset.filter(created_by__isnull=True)
    
    def perform_create(self, serializer):
        # Set created_by ke user yang sedang login
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

class LinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View untuk melihat, mengupdate, dan menghapus link
    """
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'short_code'
    
    def get_queryset(self):
        # Hanya pemilik yang bisa mengupdate/menghapus
        if self.request.user.is_authenticated:
            return Link.objects.filter(created_by=self.request.user)
        return Link.objects.filter(created_by__isnull=True)

class LinkRedirectView(APIView):
    """
    View untuk redirect short URL ke long URL
    """
    authentication_classes = []  # No authentication needed
    permission_classes = []     # No permissions needed
    
    def get(self, request, short_code):
        # Dapatkan link berdasarkan short_code
        link = get_object_or_404(Link, short_code=short_code)
        
        # Validasi link
        if not link.is_active:
            return Response(
                {"error": "This short URL has been deactivated"},
                status=status.HTTP_410_GONE
            )
        
        if link.is_expired():
            return Response(
                {"error": "This short URL has expired"},
                status=status.HTTP_410_GONE
            )
        
        # Dapatkan informasi client
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Parse user agent untuk info device
        ua_info = parse_user_agent(user_agent)
        
        # Coba dapatkan country dari IP (menggunakan service eksternal)
        country = get_country_from_ip(ip_address)
        
        # Catat klik
        LinkClick.objects.create(
            link=link,
            ip_address=anonymize_ip(ip_address),
            user_agent=user_agent,
            referrer=referrer,
            country=country,
            device_type=ua_info.get('device_type', 'Unknown') if ua_info else 'Unknown'
        )
        
        # Update click count (atomic update)
        Link.objects.filter(id=link.id).update(click_count=F('click_count') + 1)
        
        # Redirect ke URL asli
        return HttpResponseRedirect(link.long_url)

class LinkAnalyticsView(generics.RetrieveAPIView):
    """
    View untuk melihat analytics sebuah link
    """
    serializer_class = LinkAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'short_code'
    
    def get_queryset(self):
        # Hanya pemilik yang bisa melihat analytics
        if self.request.user.is_authenticated:
            return Link.objects.filter(created_by=self.request.user)
        return Link.objects.filter(created_by__isnull=True)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Hitung analytics tambahan
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Click by day
        clicks_by_day = (
            LinkClick.objects.filter(
                link=instance, 
                clicked_at__gte=thirty_days_ago
            )
            .annotate(date=TruncDate('clicked_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Click by country
        clicks_by_country = LinkClick.objects.filter(
            link=instance
        ).exclude(country__isnull=True).values('country').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Click by device
        clicks_by_device = LinkClick.objects.filter(
            link=instance
        ).exclude(device_type__isnull=True).values('device_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Tambahkan data tambahan ke context serializer
        serializer_data = serializer.data
        serializer_data['clicks_by_day'] = list(clicks_by_day)
        serializer_data['clicks_by_country'] = list(clicks_by_country)
        serializer_data['clicks_by_device'] = list(clicks_by_device)
        
        return Response(serializer_data)