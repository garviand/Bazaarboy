from django.conf.urls import patterns, include, url

index_urlpatterns = patterns('src.controllers.index', 
    url(r'^login/$', 'login', name = 'login'),
    url(r'^register/$', 'register', name = 'register'),
    url(r'^terms/$', 'terms', name = 'terms'), 
    url(r'^about/$', 'about', name = 'about'),
    url(r'^pricing/$', 'pricing', name = 'pricing'),
    url(r'^timezone/$', 'timezone', name = 'timezone'),
)

user_urlpatterns = patterns('src.controllers.user', 
    url(r'^register/$', 'register', name = 'register'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^login/$', 'login', name = 'login'),
    url(r'^auth/$', 'auth', name = 'auth'),
    url(r'^settings/$', 'settings', name = 'settings'),
    url(r'^logout/$', 'logout', name = 'logout'),
)

payment_urlpatterns = patterns('src.controllers.payment', 
    url(r'^connect/$', 'connect', name = 'connect'),
    url(r'^charge/$', 'charge', name = 'charge'),
)

profile_urlpatterns = patterns('src.controllers.profile', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^new/$', 'new', name = 'new'),
    url(r'^$', 'profile', name = 'profile'),
    url(r'^search/$', 'search', name = 'search'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^message/$', 'message', name = 'message'),
)

event_urlpatterns = patterns('src.controllers.event', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^(?P<id>\d+)/(?P<step>(basics)|(design)|(tickets)|(bonus)|(emails))/$', 
        'modify', name = 'modify'),
    url(r'^(?P<id>\d+)/manage/$', 'manage', name = 'manage'),
    url(r'^$', 'event', name = 'event'),
    url(r'^data/$', 'graph_data', name = 'graph_data'),
    url(r'^search/$', 'search', name = 'search'),
    url(r'^(?P<id>\d+)/invite/$', 'invite', name = 'invite'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
    url(r'^launch/$', 'launch', name = 'launch'),
    url(r'^delaunch/$', 'delaunch', name = 'delaunch'),
    url(r'^organizer/add/$', 'add_organizer', name = 'add_organizer'),
    url(r'^organizer/delete/$', 'delete_organizer', name = 'delete_organizer'),
    url(r'^ticket/$', 'ticket', name = 'ticket'), 
    url(r'^ticket/create/$', 'create_ticket', name = 'ticket-create'),
    url(r'^ticket/edit/$', 'edit_ticket', name = 'ticket-edit'),
    url(r'^ticket/delete/$', 'delete_ticket', name = 'ticket-delete'),
    url(r'^tickets/reorder/$', 'reorder_tickets', name = 'tickets-reorder'),
    url(r'^promo/create/$', 'create_promo', name = 'promo-create'),
    url(r'^promo/edit/$', 'edit_promo', name = 'promo-edit'),
    url(r'^promo/delete/$', 'delete_promo', name = 'promo-delete'),
    url(r'^purchase/$', 'purchase', name = 'purchase'),
    url(r'^purchase/add/$', 'add_purchase', name = 'purchase-add'),
    url(r'^export/$', 'export', name = 'export'),
    url(r'^checkin/$', 'checkin', name = 'checkin'),
)

sponsorship_urlpatterns = patterns('src.controllers.sponsorship', 
    url(r'^criteria/create/$', 'create_criteria', name = 'criteria-create'), 
    url(r'^criteria/edit/$', 'edit_criteria', name = 'criteria-edit'), 
    url(r'^criteria/delete/$', 'delete_criteria', name = 'criteria-delete'), 
    url(r'^create/$', 'create', name = 'create'),
    url(r'^delete/$', 'delete', name = 'delete'), 
)

bonus_urlpatterns = patterns('src.controllers.bonus', 
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'), 
    url(r'^delete/$', 'delete', name = 'delete'), 
    url(r'^send/$', 'send', name = 'send'), 
    url(r'^claim/$', 'claim', name = 'claim'), 
)

file_urlpatterns = patterns('src.controllers.file', 
    url(r'^image/upload/$', 'upload_image', name = 'image-upload'),
    url(r'^image/crop/$', 'crop_image', name = 'image-crop'),
    url(r'^image/delete/$', 'delete_image', name = 'image-delete'),
    url(r'^aviary/$', 'aviary', name = 'aviary'),
)

admin_urlpatterns = patterns('src.controllers.admin.admin', 
    url(r'^$', 'index', name = 'index'),
    url(r'^login/$', 'login', name = 'login'),
    url(r'^auth/$', 'auth', name = 'auth'),
    url(r'^logout/$', 'logout', name = 'logout'),
    url(r'^login/profile/$', 'login_profile', name = 'login_profile'),
)

urlpatterns = patterns('',
    url(r'^$', 'src.controllers.index.index', name = 'index'),
    url(r'^', include(index_urlpatterns, namespace = 'index')),
    url(r'^user/', include(user_urlpatterns, namespace = 'user')),
    url(r'^payment/', include(payment_urlpatterns, namespace = 'payment')),
    url(r'^profile/', include(profile_urlpatterns, namespace = 'profile')),
    url(r'^event/', include(event_urlpatterns, namespace = 'event')),
    url(r'^sponsorship/', 
        include(sponsorship_urlpatterns, namespace = 'sponsorship')),
    url(r'^bonus/', include(bonus_urlpatterns, namespace = 'bonus')), 
    url(r'^file/', include(file_urlpatterns, namespace = 'file')),
    url(r'^admin/', include(admin_urlpatterns, namespace = 'admin')),
    url(r'^(?P<id>[A-Za-z0-9-]+)/$', 'src.controllers.event.index', name = 'event-slug'),
)

handler404 = 'src.controllers.index.pageNotFound'
handler500 = 'src.controllers.index.serverError'