from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from django.conf import settings


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'toolshare_trunk.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'^app/', include('ToolShare.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^a/', include('accounts.urls')),
    url(r'^notifications/', include('notifications.urls')),

    url(r'^$', lambda x: HttpResponseRedirect('/app/dashboard'),)
)

if settings.DEBUG:
    # enable local preview of error pages
    urlpatterns += patterns('',
        (r'^403/$', TemplateView.as_view(template_name="403.html")),
        (r'^404/$', TemplateView.as_view(template_name="404.html")),
        (r'^500/$', TemplateView.as_view(template_name="500.html")),
    )
