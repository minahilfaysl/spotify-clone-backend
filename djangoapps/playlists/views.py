from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from djangoapps.playlists.models import Playlist, Track
from djangoapps.playlists.serializers import (
    PlaylistSerializer,
    TrackSerializer,
)
from djangoapps.userdata.pagination import HomePagination


class PlaylistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing playlists
    """
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['user__username', 'is_private']

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


class TrackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing tracks in playlists
    """
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['playlist']
    # ordering_fields = ['album_publish_year']
