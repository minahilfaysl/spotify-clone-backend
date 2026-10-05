from django.conf.urls import url
from rest_framework import routers
from djangoapps.playlists.views import (
    PlaylistViewSet,
    TrackViewSet,
)

router = routers.SimpleRouter()
router.register(r'playlists', PlaylistViewSet)
router.register(r'tracks', TrackViewSet)

urlpatterns = [
    # get recently released albums for homepage
    url(r'^playlist/new_playlists',
        PlaylistViewSet.as_view({'get': 'new_playlists'}),
        name='new_playlists'),
]

urlpatterns = router.urls
