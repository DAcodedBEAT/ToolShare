from django.conf.urls import patterns, url
from accounts import views

from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect


urlpatterns = patterns('',
    url(r'^$', lambda x: HttpResponseRedirect('/a/my_account')),
    url(r'^my_account/$', views.my_account, name='my_account'),
    url(r'^users/(?P<u_id>[^/]+)/$', views.view_user, name='view_user'),
    url(r'^create_profile/$', views.create_profile, name='create_profile'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^register/$', views.user_register, name='register'),
    url(r'^delete_user/$', views.deactivate_user, name='deactivate_user'),
    url(r'^locations/$', views.location, name='locations'),
) #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)
