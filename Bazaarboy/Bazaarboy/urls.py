from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^$', 'src.controllers.landing.index', 
        name = 'Landing'),

    # User

    url(r'^user/create/$', 'src.controllers.user.create', 
        name = 'User-create'),

    # City

    url(r'^city/$', 'src.controllers.community.city', name = 'City'),
    url(r'^city/create/$', 'src.controllers.community.create_city', 
        name = 'City-create'),

    # Community

    url(r'^community/$', 'src.controllers.community.community', 
        name = 'Community'),
    url(r'^community/create/$', 'src.controllers.community.create_community', 
        name = 'Community-create'),

)