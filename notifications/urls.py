from django.conf.urls import patterns, include, url
from django.shortcuts import redirect

urlpatterns = patterns('',
    url(r'^$', lambda x: redirect('notifications.views.inbox')),
    url(r'^show/(?P<notif_id>\d+)/$', 'notifications.views.show_notif', name='show_notif'),
    url(r'^read/(?P<notif_id>\d+)/$', 'notifications.views.viewed_notif', name='viewed_notif'),
    url(r'^unread/(?P<notif_id>\d+)/$', 'notifications.views.not_viewed_notif', name='not_viewed_notif'),
    url(r'^delete/(?P<notif_id>\d+)/$', 'notifications.views.delete_notif', name='delete_notif'),

    url(r'^approve_request/(?P<cid>\d+)/$', 'notifications.views.approve_checkout', name='approve_checkout'),
    url(r'^deny_request/(?P<cid>\d+)/$', 'notifications.views.deny_checkout', name='deny_checkout'),

    url(r'^inbox/$', 'notifications.views.inbox', name='inbox_notif'),
    url(r'^sent/$', 'notifications.views.outbox', name='sent_notif'),
    url(r'^unread_inbox/$', 'notifications.views.unread_inbox', name='unread_inbox_notif'),
    url(r'^unread_request/$', 'notifications.views.unread_checkout', name='unread_checkout_notif'),
    url(r'^checkout_inbox/$', 'notifications.views.checkout_inbox', name='checkout_inbox_notif'),
    url(r'^compose/$', 'notifications.views.compose', name='compose_notif'),
)