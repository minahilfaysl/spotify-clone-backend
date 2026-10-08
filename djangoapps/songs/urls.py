from django.urls import re_path
from rest_framework import routers
from djangoapps.songs.views import (
    SongViewSet,
    AlbumViewSet,
    GenreViewSet,
)

router = routers.SimpleRouter()
router.register(r'songs', SongViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'genre', GenreViewSet)

urlpatterns = [
    # get recently released albums for homepage
    re_path(r'^albums/new_releases',
        SongViewSet.as_view({'get': 'new_releases'}),
        name='new_releases'),
    # increments streams for a song when called
    re_path(r'^songs/<int:pk>/increment_streams',
        SongViewSet.as_view({'get': 'increment_streams'}),
        name='song-increment-streams'),
    re_path(r'^songs/<str:username>/get_top_tracks',
        SongViewSet.as_view({'get': 'get_top_tracks'}),
        name='get-top-tracks'),
]

urlpatterns = router.urls
