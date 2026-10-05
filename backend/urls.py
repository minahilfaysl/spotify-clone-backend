from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('djangoapps.users.urls')),
    path('api/token/', include('rest_framework.urls',
                               namespace='rest_framework')),
    path('api/', include('djangoapps.songs.urls')),
    path('api/', include('djangoapps.playlists.urls')),
    path('api/userdata/', include('djangoapps.userdata.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
