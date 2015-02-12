from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

from ToolShare import views

urlpatterns = patterns('',

    url(r'^browse', views.browse_tools, name='browse'),
    url(r'^tools/(?P<tool_id>\d+)/$', views.view_tool, name='view_tool'),
    url(r'^tools/add_tool/$', views.add_tool, name='add_tool'),
    url(r'^checkout/(?P<tool_id>\d+)/$', views.checkout_tool),
    url(r'^checkout/cancel/(?P<tool_id>\d+)/$', views.cancel_Checkout),
    url(r'^tools/delete/(?P<tool_id>\d+)/$', views.delete_tool, name='delete_tool'),
    url(r'^tools/flag/(?P<tool_id>\d+)/$', views.flag_tool, name='flag_tool'),
    url(r'^tools/confirm_delete/(?P<tool_id>\d+)/$', views.confirm_delete_tool, name='confirm_delete_tool'),
    url(r'^tools/edit/(?P<tool_id>\d+)/$', views.edit_tool,name= 'edit_tool'),
    url(r'^checkout/check_in/', views.checkout_tool, name='check_in'),

    url(r'^dashboard/', views.dashboard, name='dashboard'),

    url(r'^add_cat/', views.add_cat),

    url(r'^$', views.index)
) + static('/static/', document_root='static')