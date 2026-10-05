from django.db.models import F
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from djangoapps.songs.models import Song, Album, Genre
from djangoapps.songs.serializers import (
    SongSerializer,
    AlbumSerializer,
    GenreSerializer
)
from djangoapps.userdata.pagination import HomePagination
from djangoapps.users.permissions import IsArtist
from django.contrib.auth import get_user_model
User = get_user_model()


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AlbumViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing albums
    GET /api/albums/?artist__username={username}
    """
    queryset = Album.objects.prefetch_related('artist')
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsArtist]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['artist__username']
    ordering_fields = ['album_publish_year']

    @action(detail=False, methods=['get'])
    def new_releases(self, request):
        ''' return only 10 recent objects for homepage '''
        self.pagination_class = HomePagination
        queryset = Album.objects.all().order_by('-album_publish_year')
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
    queryset = Song.objects.prefetch_related('album')
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsArtist]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['album', 'album__artist', 'album__genre']
    ordering_fields = ['track_number', 'album__album_publish_year']
    lookup_field = 'username'

    # print(SongSerializer(queryset, many=True).data)

    @action(detail=True, methods=['get'])
    def increment_streams(self, request, username=None):
        """
        GET api/songs/<int:pk>/increment_streams
        using `get` as it is a safe method and any user can increment a stream
        """
        queryset = Song.objects.filter(id=username)
        # increment total streams
        queryset.update(total_streams=F("total_streams") + 1)

        serializer_class = SongSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer_class.data)

    @action(detail=True, methods=['get'])
    def get_top_tracks(self, request, username=None):
        """
        GET api/songs/<str:username>/top_tracks
        to get the four most streamed songs by an artist
        """
        user = User.objects.filter(username=username).first()
        queryset = (Song.objects
                        .filter(album__artist__id=user.id)
                        .order_by('-total_streams')[:5])
        serializer_class = SongSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response({"results": serializer_class.data})
