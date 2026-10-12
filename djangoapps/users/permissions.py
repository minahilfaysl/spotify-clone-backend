from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_demo_account(user):
    return bool(user and user.is_authenticated
                and user.username in settings.DEMO_READ_ONLY_USERS)


class IsArtist(BasePermission):
    '''
    Only artists can create songs and albums, and only the album's artist can
    edit or delete it (or its songs).
    '''
    message = 'Only artists can upload or edit music.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_artist

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # albums have an artist; songs reach it through their album
        artist_id = obj.artist_id if hasattr(obj, 'artist_id') else obj.album.artist_id
        return artist_id == request.user.id


class IsOwnerOrReadOnly(BasePermission):
    '''Anyone can read; only the owner (obj.user) can change or delete.'''
    message = 'You can only change your own content.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class IsSelf(BasePermission):
    '''For endpoints acting on a User object: only that user may use them.'''
    message = 'You can only change your own account.'

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class DemoAccountsReadOnly(BasePermission):
    '''
    The shared demo logins are public, so in production they can browse and
    play but not change or delete the seeded content. Configure with the
    DEMO_READ_ONLY_USERS setting.
    '''
    message = ('Demo accounts are read-only so everyone sees the same demo. '
               'Sign up for your own account to try uploading and editing.')

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return not is_demo_account(request.user)


class OwnsUserDataInURL(BasePermission):
    '''
    For /api/userdata/<endpoint>/<username>/ routes: changes are only allowed
    on your own username, and so are reads unless the view sets
    `public_read = True` (e.g. followers, following).
    Listing every user's data is never allowed.
    '''
    message = 'You can only access your own library, likes and history.'

    def has_permission(self, request, view):
        if getattr(view, 'action', None) == 'list':
            return False
        username = view.kwargs.get('user__username')
        if username is None:
            return True
        if request.method in SAFE_METHODS and getattr(view, 'public_read', False):
            return True
        return request.user.is_authenticated and request.user.username == username
