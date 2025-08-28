from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission untuk hanya mengizinkan pemilik objek untuk mengeditnya.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions diizinkan untuk semua request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions hanya diizinkan untuk pemilik link
        return obj.created_by == request.user

class IsOwner(permissions.BasePermission):
    """
    Custom permission untuk hanya mengizinkan pemilik objek untuk mengaksesnya.
    """
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class CanEditLink(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Izin baca (GET, HEAD, OPTIONS) selalu diberikan
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user

        if user and user.is_authenticated:
            # Untuk user yang login, mereka harus menjadi pemilik link
            return obj.created_by == user
        else:
            # Untuk user anonim, mereka harus mengirim edit_key yang benar
            # dari header 'X-Edit-Key'
            edit_key_from_header = request.headers.get('X-Edit-Key')
            if not edit_key_from_header:
                return False
            return obj.edit_key == edit_key_from_header