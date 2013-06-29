from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    # Index

    url(r'^$', 'src.controllers.index.index', name = 'index'),

    # User

    url(r'^user/register/$', 'src.controllers.user.register', 
        name = 'user-register'),
    url(r'^user/create/$', 'src.controllers.user.create', 
        name = 'user-create'),
    url(r'^user/login/$', 'src.controllers.user.login', name = 'user-login'),
    url(r'^user/auth/$', 'src.controllers.user.auth', name = 'user-auth'),
    url(r'^user/logout/$', 'src.controllers.user.logout', name = 'user-logout'),

    # WePay

    url(r'^wepay/authorize/$', 'src.controllers.wepay.authorize', 
        name = 'wepay-authorize'),
    url(r'^wepay/create/$', 'src.controllers.wepay.create', 
        name = 'wepay-create'),

    # City

    url(r'^city/$', 'src.controllers.city.city', name = 'city'),
    url(r'^city/create/$', 'src.controllers.city.create', 
        name = 'city-create'),

    # Community

    url(r'^community/$', 'src.controllers.community.community', 
        name = 'community'),
    url(r'^community/create/$', 'src.controllers.community.create', 
        name = 'community-create'),

    # Profile

    url(r'^profile/create/$', 'src.controllers.profile.create', 
        name = 'Profile-create'),

    # Events

    url(r'^event/(?P<id>\d+)/$', 'src.controllers.event.index', 
        name = 'event-normal'),
    url(r'^event/create/$', 'src.controllers.event.create', 
        name = 'event-normal-create'),
    url(r'^event/ticket/create/$', 'src.controllers.event.create_ticket', 
        name = 'event-normal-ticket-create'),
    url(r'^event/ticket/delete/$', 'src.controllers.event.delete_ticket', 
        name = 'event-normal-ticket-delete'),

    url(r'^initiative/(?P<id>\d+)/$', 'src.controllers.initiative.index', 
        name = 'event-initiative'),
    url(r'^initiative/create/$', 'src.controllers.initiative.create', 
        name = 'event-initiative-create'),

)