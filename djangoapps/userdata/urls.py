from django.conf.urls import url
from django.urls import path
from rest_framework import routers
from djangoapps.userdata.views import (
    LikedAlbumsViewSet,
    LikedSongsViewSet,
    LikedPlaylistsViewSet,
    RecentlyPlayedViewSet,
    UserLibraryViewSet,
    FollowersViewSet,
    FollowingViewSet,
    RetrieveSearchResultsView,
)

router = routers.SimpleRouter()
router.register(r'liked_albums', LikedAlbumsViewSet, basename='liked_albums')
router.register(r'liked_songs', LikedSongsViewSet, basename='liked_songs')
router.register(r'liked_playlists', LikedPlaylistsViewSet, basename='liked_playlists')
router.register(r'recently_played', RecentlyPlayedViewSet, basename='recently_played')
router.register(r'user_library', UserLibraryViewSet, basename='user_library')
router.register(r'followers', FollowersViewSet, basename='followers')
router.register(r'following', FollowingViewSet, basename='following')

urlpatterns = [
    # returns list of artists
    url(r'^user_library/<str:user__username>/retrieve_artists',
        UserLibraryViewSet.as_view({'put': 'retrieve_artists'}),
        name='retrieve-artists'),

    # updates recently played albums list
    url(r'^recently_played/<str:user__username>/update_albums',
        RecentlyPlayedViewSet.as_view({'put': 'update_albums'}),
        name='update-recents-album'),

    # updates recently played playlists list
    url(r'^recently_played/<str:user__username>/update_playlists',
        RecentlyPlayedViewSet.as_view({'put': 'update_playlists'}),
        name='update-recents-playlist'),

    # search results
    path('search/<str:keyword>/', RetrieveSearchResultsView.as_view(),
         name='search'),
]

urlpatterns += router.urls
