from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    # Index

    url(r'^$', 'src.controllers.landing.index', name = 'index'),

    # User

    url(r'^user/register/$', 'src.controllers.user.register', 
        name = 'user-register'),
    url(r'^user/create/$', 'src.controllers.user.create', 
        name = 'user-create'),
    url(r'^user/login/$', 'src.controllers.user.login', name = 'user-login'),
    url(r'^user/auth/$', 'src.controllers.user.auth', name = 'user-auth'),
    url(r'^user/logout/$', 'src.controllers.user.logout', name = 'user-logout'),

    # City

    url(r'^city/$', 'src.controllers.community.city', name = 'city'),
    url(r'^city/create/$', 'src.controllers.community.create_city', 
        name = 'city-create'),

    # Community

    url(r'^community/$', 'src.controllers.community.community', 
        name = 'community'),
    url(r'^community/create/$', 'src.controllers.community.create_community', 
        name = 'community-create'),

    # Profile

    url(r'^profile/create/$', 'src.controllers.profile.create', 
        name = 'Profile-create'),

    # Events

    url(r'^event/(?P<id>\d+)/$', 'src.controllers.event.index', name = 'event'),

)