from django.conf.urls import patterns, include, url

index_urlpatterns = patterns('src.controllers.index', 
    url(r'^terms/$', 'terms', name = 'terms'), 
    url(r'^about/$', 'about', name = 'about'),
    url(r'^timezone/$', 'timezone', name = 'timezone'),
)

user_urlpatterns = patterns('src.controllers.user', 
    url(r'^register/$', 'register', name = 'register'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^login/$', 'login', name = 'login'),
    url(r'^auth/$', 'auth', name = 'auth'),
    url(r'^fbAuth/$', 'fbAuth', name = 'fbAuth'),
    url(r'^settings/$', 'settings', name = 'settings'),
    url(r'^logout/$', 'logout', name = 'logout'),
)

wepay_urlpatterns = patterns('src.controllers.wepay', 
    url(r'^authorize/$', 'authorize', name = 'authorize'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^ipn/$', 'ipn', name = 'ipn'),
)

city_urlpatterns = patterns('src.controllers.city',
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^$', 'city', name = 'city'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
)

community_urlpatterns = patterns('src.controllers.community', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^$', 'community', name = 'community'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
)

profile_urlpatterns = patterns('src.controllers.profile', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^manage/$', 'manage', name = 'manage'),
    url(r'^$', 'profile', name = 'profile'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
)

event_urlpatterns = patterns('src.controllers.event', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^new/$', 'new', name = 'new'),
    url(r'^$', 'event', name = 'event'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
    url(r'^launch/$', 'launch', name = 'launch'),
    url(r'^delaunch/$', 'delaunch', name = 'delaunch'),
    url(r'^ticket/create/$', 'create_ticket', name = 'ticket-create'),
    url(r'^ticket/edit/$', 'edit_ticket', name = 'ticket-edit'),
    url(r'^ticket/delete/$', 'delete_ticket', name = 'ticket-delete'),
    url(r'^purchase/$', 'purchase', name = 'purchase'),
)

fundraiser_urlpatterns = patterns('src.controllers.fundraiser', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^$', 'fundraiser', name = 'fundraiser'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
    url(r'^launch/$', 'launch', name = 'launch'),
    url(r'^delaunch/$', 'delaunch', name = 'delaunch'),
    url(r'^reward/create/$', 'create_reward', name = 'reward-create'),
    url(r'^reward/edit/$', 'edit_reward', name = 'reward-edit'),
    url(r'^reward/delete/$', 'delete_reward', name = 'reward-delete'),
    url(r'^donate/$', 'donate', name = 'donate'),
)

sponsorship_urlpatterns = patterns('src.controllers.sponsorship', 
    url(r'^create/$', 'create', name = 'create'),
)

file_urlpatterns = patterns('src.controllers.file', 
    url(r'^image/upload/$', 'upload_image', name = 'image-upload'),
    url(r'^image/crop/$', 'crop_image', name = 'image-crop'),
    url(r'^image/delete/$', 'delete_image', name = 'image-delete'),
)

admin_urlpatterns = patterns('src.controllers.admin.admin', 
    url(r'^$', 'index', name = 'index'),
    url(r'^login/$', 'login', name = 'login'),
    url(r'^auth/$', 'auth', name = 'auth'),
    url(r'^logout/$', 'logout', name = 'logout'),
)

urlpatterns = patterns('',
    url(r'^$', 'src.controllers.index.index', name = 'index'),
    url(r'^', include(index_urlpatterns, namespace = 'index')),
    url(r'^user/', include(user_urlpatterns, namespace = 'user')),
    url(r'^wepay/', include(wepay_urlpatterns, namespace = 'wepay')),
    url(r'^city/', include(city_urlpatterns, namespace = 'city')),
    url(r'^community/', 
        include(community_urlpatterns, namespace = 'community')),
    url(r'^profile/', include(profile_urlpatterns, namespace = 'profile')),
    url(r'^event/', include(event_urlpatterns, namespace = 'event')),
    url(r'^fundraiser/', 
        include(fundraiser_urlpatterns, namespace = 'fundraiser')),
    url(r'^sponsorship/', 
        include(sponsorship_urlpatterns, namespace = 'sponsorship')),
    url(r'^file/', include(file_urlpatterns, namespace = 'file')),
    url(r'^admin/', include(admin_urlpatterns, namespace = 'admin')),
)

handler404 = 'src.controllers.index.pageNotFound'
handler500 = 'src.controllers.index.serverError'