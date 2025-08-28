from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import shortuuid
from datetime import timedelta

class Link(models.Model):
    short_code = models.CharField(max_length=20, unique=True, db_index=True)
    edit_key = models.CharField(max_length=40, unique=True, default=shortuuid.uuid)
    long_url = models.URLField(max_length=2000)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    click_count = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = shortuuid.ShortUUID().random(length=8)
        
        if not self.expires_at and not self.pk:  # Hanya untuk objek baru
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

class LinkClick(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True, max_length=2000)
    country = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        ordering = ['-clicked_at']