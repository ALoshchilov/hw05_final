from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler403 = 'core.views.page_permission_denied'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.page_internal_server_error'

urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    # Встроенная админка Django
    path('admin/', admin.site.urls, name='admin'),
    # urls для кастомного приложения users
    path('auth/', include('users.urls', namespace='users')),
    # urls модуля для управления пользователями
    path('auth/', include('django.contrib.auth.urls')),
    # Главная страница
    path('', include('posts.urls', namespace='posts')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
