from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from djangoapps.songs.models import Song, Album, Genre
from djangoapps.songs.serializers import (
    SongSerializer,
    AlbumSerializer,
    GenreSerializer
)
from djangoapps.userdata.pagination import HomePagination
from djangoapps.users.permissions import IsArtist, DemoAccountsReadOnly
from django.contrib.auth import get_user_model
User = get_user_model()


class GenreViewSet(viewsets.ModelViewSet):
    '''Anyone can read genres; only admins can create, edit or delete them.'''
    queryset = Genre.objects.order_by('id')
    serializer_class = GenreSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return []
        return [IsAdminUser(), DemoAccountsReadOnly()]


class AlbumViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing albums
    GET /api/albums/?artist__username={username}
    """
    queryset = Album.objects.select_related('artist', 'genre')
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsArtist, DemoAccountsReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['artist__username']
    ordering_fields = ['album_publish_year']
    ordering = ['-album_publish_year', 'id']  # stable pagination by default

    def perform_create(self, serializer):
        # an album always belongs to the artist creating it
        serializer.save(artist=self.request.user)

    @action(detail=False, methods=['get'])
    def new_releases(self, request):
        ''' return only 10 recent objects for homepage '''
        self.pagination_class = HomePagination
        queryset = self.get_queryset().order_by('-album_publish_year')
        page = self.paginate_queryset(queryset)
        serializer = AlbumSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SongViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing songs.
    GET /api/songs/?album={pk}
    """
    queryset = Song.objects.select_related('album__artist', 'album__genre')
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsArtist, DemoAccountsReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['album', 'album__artist', 'album__genre']
    ordering_fields = ['track_number', 'album__album_publish_year']
    ordering = ['id']  # stable pagination by default

    def get_permissions(self):
        if self.action == 'increment_streams':
            # any signed-in listener (not just artists) counts a play
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def increment_streams(self, request, pk=None):
        """
        POST api/songs/<int:pk>/increment_streams/
        Counts one play. POST, not GET: GET requests must not change data
        (browsers, crawlers and caches may repeat them).
        """
        song = get_object_or_404(Song, pk=pk)
        # atomic in the database: UPDATE ... SET total_streams = total_streams + 1
        Song.objects.filter(pk=song.pk).update(total_streams=F("total_streams") + 1)
        song.refresh_from_db()
        serializer = SongSerializer(song, context={'request': request})
        return Response([serializer.data])

    @action(detail=True, methods=['get'])
    def get_top_tracks(self, request, pk=None):
        """
        GET api/songs/<username>/get_top_tracks/
        the five most streamed songs by an artist (the URL segment is the
        artist's username)
        """
        artist = get_object_or_404(User, username=pk)
        queryset = (self.get_queryset()
                    .filter(album__artist=artist)
                    .order_by('-total_streams')[:5])
        serializer_class = SongSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response({"results": serializer_class.data})
