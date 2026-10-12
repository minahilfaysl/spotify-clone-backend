from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from djangoapps.playlists.models import Playlist, Track
from djangoapps.playlists.serializers import (
    PlaylistSerializer,
    TrackSerializer,
)
from djangoapps.userdata.pagination import HomePagination
from djangoapps.users.permissions import IsOwnerOrReadOnly, DemoAccountsReadOnly


def visible_playlists(user):
    '''Public playlists, plus the user's own private ones.'''
    if user.is_authenticated:
        return Playlist.objects.filter(Q(is_private=False) | Q(user=user))
    return Playlist.objects.filter(is_private=False)


class PlaylistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing playlists.
    Anyone can see public playlists; private ones are only visible to their
    owner, and only the owner can change or delete a playlist.
    """
    # used by the router for naming; get_queryset() decides what each user sees
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, DemoAccountsReadOnly]
    filterset_fields = ['user__username', 'is_private']

    def get_queryset(self):
        return (visible_playlists(self.request.user)
                .select_related('user').order_by('-date_created', 'id'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def new_playlists(self, request):
        ''' return only 10 recent objects for homepage '''
        self.pagination_class = HomePagination
        queryset = Playlist.objects.filter(
            is_private=False
        ).order_by('-date_created')
        page = self.paginate_queryset(queryset)
        serializer = PlaylistSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IsPlaylistOwnerOrReadOnly(IsOwnerOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.playlist)


class TrackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing tracks in playlists.
    Only the playlist's owner can add or remove tracks.
    """
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsPlaylistOwnerOrReadOnly, DemoAccountsReadOnly]
    filterset_fields = ['playlist']

    def get_queryset(self):
        return (Track.objects
                .filter(playlist__in=visible_playlists(self.request.user))
                .select_related('playlist', 'song__album__artist', 'song__album__genre'))
