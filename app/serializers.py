from rest_framework import serializers
from .models import Link, LinkClick
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth.models import User

class LinkSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Link
        fields = [
            'id', 'short_code', 'long_url', 'short_url', 
            'created_at', 'expires_at', 'is_active', 
            'click_count', 'title', 'is_expired', 'created_by',
        ]
        read_only_fields = ['short_code', 'created_at', 'click_count', 'created_by']
    
    def get_short_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/r/{obj.short_code}/')
        return f'/r/{obj.short_code}/'
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def validate_long_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value
    
    def validate(self, data):
        expires_at = data.get('expires_at')
        if expires_at and expires_at < timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return data

    def update(self, instance, validated_data):
        if instance.created_by is None:
            raise serializers.ValidationError(
                "This data cannot be updated because Created_by is null."
            )
        return super().update(instance, validated_data)

class LinkClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkClick
        fields = ['clicked_at', 'ip_address', 'user_agent', 'referrer', 'country', 'device_type']

class LinkAnalyticsSerializer(serializers.ModelSerializer):
    clicks = LinkClickSerializer(many=True, read_only=True)
    clicks_by_day = serializers.SerializerMethodField()
    clicks_by_country = serializers.SerializerMethodField()
    clicks_by_device = serializers.SerializerMethodField()
    
    class Meta:
        model = Link
        fields = [
            'short_code', 'long_url', 'click_count', 'created_at',
            'clicks', 'clicks_by_day', 'clicks_by_country', 'clicks_by_device'
        ]
    
    def get_clicks_by_day(self, obj):
        return self.context.get('clicks_by_day', [])
    
    def get_clicks_by_country(self, obj):
        return self.context.get('clicks_by_country', [])
    
    def get_clicks_by_device(self, obj):
        return self.context.get('clicks_by_device', [])


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
