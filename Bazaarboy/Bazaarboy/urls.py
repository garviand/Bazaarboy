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
    url(r'^create/$', 'create', name = 'create'),
    url(r'^reset/$', 'reset', name = 'reset'),
    url(r'^reset/create/$', 'create_reset', name = 'create_reset'),
    url(r'^password/change/$', 'change_password', name = 'change_password'),
    url(r'^auth/$', 'auth', name = 'auth'),
    url(r'^settings/$', 'settings', name = 'settings'),
    url(r'^unsub/$', 'unsubscribe', name = 'unsubscribe'),
    url(r'^logout/$', 'logout', name = 'logout'),
)

payment_urlpatterns = patterns('src.controllers.payment', 
    url(r'^connect/$', 'connect', name = 'connect'),
    url(r'^charge/$', 'charge', name = 'charge'),
    url(r'^refund/$', 'refund', name = 'refund'),
    url(r'^charge/invite/$', 'charge_invite', name = 'charge-invite'),
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

list_urlpatterns = patterns('src.controllers.list', 
    url(r'^$', 'index', name = 'index'),
    url(r'^(?P<lt>\d+)/$', 'list', name = 'list'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^delete/$', 'delete', name = 'delete'),
    url(r'^add/item/$', 'add_item', name = 'add_item'),
    url(r'^remove/item/$', 'remove_item', name = 'remove_item'),
    url(r'^add/event/$', 'add_from_event', name = 'add_from_event'),
    url(r'^add/csv/$', 'add_from_csv', name = 'add_from_csv'),
    url(r'^csv/prepare/$', 'prepare_csv', name = 'prepare_csv'),
)

event_urlpatterns = patterns('src.controllers.event', 
    url(r'^(?P<id>\d+)/$', 'index', name = 'index'),
    url(r'^(?P<id>\d+)/(?P<step>(basics)|(design)|(tickets)|(bonus)|(emails))/$', 
        'modify', name = 'modify'),
    url(r'^(?P<id>\d+)/embed/$', 'ticket_embed', name = 'ticket-embed'),
    url(r'^(?P<id>\d+)/manage/$', 'manage', name = 'manage'),
    url(r'^$', 'event', name = 'event'),
    url(r'^data/$', 'graph_data', name = 'graph_data'),
    url(r'^search/$', 'search', name = 'search'),
    url(r'^(?P<event>\d+)/invite/$', 'invite', name = 'invite'),
    url(r'^(?P<event>\d+)/invite/create/$', 'create_invite', name = 'create-invite'),
    url(r'^invite/new/$', 'new_invite', name = 'new-invite'),
    url(r'^invite/save/$', 'save_invite', name = 'save-invite'),
    url(r'^invite/delete/$', 'delete_invite', name = 'delete-invite'),
    url(r'^invite/send/$', 'send_invite', name = 'send-invite'),
    url(r'^invite/(?P<invite>\d+)/details/$', 'invite_details', name = 'invite-details'),
    url(r'^invite/(?P<invite>\d+)/copy/$', 'copy_invite', name = 'invite-copy'),
    url(r'^invite/(?P<invite>\d+)/edit/$', 'edit_invite', name = 'edit-invite'),
    url(r'^invite/(?P<invite>\d+)/preview/$', 'preview_invite', name = 'preview-invite'),
    url(r'^invite/(?P<invite>\d+)/preview/template/$', 'preview_invite_template', name = 'preview-invite-template'),
    url(r'^(?P<id>\d+)/manualinvite/$', 'manual_invite', name = 'manual-invite'), # To Be Depreciated
    url(r'^(?P<event>\d+)/followup/$', 'follow_up', name = 'follow-up'),
    url(r'^(?P<event>\d+)/followup/create/$', 'create_follow_up', name = 'create-follow-up'),
    url(r'^followup/new/$', 'new_follow_up', name = 'new-follow-up'),
    url(r'^followup/save/$', 'save_follow_up', name = 'save-follow-up'),
    url(r'^followup/delete/$', 'delete_follow_up', name = 'delete-follow-up'),
    url(r'^followup/(?P<follow_up>\d+)/edit/$', 'edit_follow_up', name = 'edit-follow-up'),
    url(r'^followup/(?P<follow_up>\d+)/preview/$', 'preview_follow_up', name = 'preview-follow-up'),
    url(r'^followup/(?P<follow_up>\d+)/preview/template/$', 'preview_follow_up_template', name = 'preview-follow-up-template'),
    url(r'^followup/attachment/$', 'follow_up_attachment', name = 'attachment-follow-up'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^edit/$', 'edit', name = 'edit'),
    url(r'^delete/$', 'delete', name = 'delete'),
    url(r'^launch/$', 'launch', name = 'launch'),
    url(r'^delaunch/$', 'delaunch', name = 'delaunch'),
    url(r'^organizer/request/$', 'request_organizer', name = 'request_organizer'),
    url(r'^organizer/request/accept/$', 'accept_organizer_request', name = 'accept_organizer_request'),
    url(r'^organizer/request/reject/$', 'reject_organizer_request', name = 'reject_organizer_request'),
    url(r'^organizer/add/$', 'add_organizer', name = 'add_organizer'),
    url(r'^organizer/delete/$', 'delete_organizer', name = 'delete_organizer'),
    url(r'^ticket/$', 'ticket', name = 'ticket'), 
    url(r'^ticket/create/$', 'create_ticket', name = 'ticket-create'),
    url(r'^ticket/edit/$', 'edit_ticket', name = 'ticket-edit'),
    url(r'^ticket/delete/$', 'delete_ticket', name = 'ticket-delete'),
    url(r'^promo/$', 'promo', name = 'promo'),
    url(r'^promo/create/$', 'create_promo', name = 'promo-create'),
    url(r'^promo/edit/$', 'edit_promo', name = 'promo-edit'),
    url(r'^promo/delete/$', 'delete_promo', name = 'promo-delete'),
    url(r'^promo/link/$', 'link_promo', name = 'promo-link'),
    url(r'^promo/unlink/$', 'unlink_promo', name = 'promo-unlink'),
    url(r'^tickets/reorder/$', 'reorder_tickets', name = 'tickets-reorder'),
    url(r'^set_attachment/$', 'set_attachment', name = 'set-attachment'),
    url(r'^remove_attachment/$', 'remove_attachment', name = 'remove-attachment'),
    url(r'^issue/$', 'issue', name = 'issue'),
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
    url(r'^csv/upload/$', 'upload_csv', name = 'csv-upload'),
    url(r'^aviary/$', 'aviary', name = 'aviary'),
)

admin_urlpatterns = patterns('src.controllers.admin.admin', 
    url(r'^$', 'index', name = 'index'),
    url(r'^login/$', 'login', name = 'login'),
    url(r'^auth/$', 'auth', name = 'auth'),
    url(r'^logout/$', 'logout', name = 'logout'),
    url(r'^login/profile/$', 'login_profile', name = 'login_profile'),
    url(r'^event/premium/$', 'make_premium', name = 'make_premium'),
    url(r'^event/premium/undo/$', 'undo_premium', name = 'undo_premium'),
)

designs_urlpatterns = patterns('src.controllers.designs.designs', 
    url(r'^$', 'index', name = 'index'),
    url(r'^create/$', 'create', name = 'create'),
    url(r'^project/create/$', 'create_project', name = 'create_project'),
    url(r'^project/charge/$', 'charge', name = 'charge'),
    url(r'^project/finalize/$', 'finalize_project', name = 'finalize_project'),
    url(r'^project/download/$', 'download_final', name = 'download_final'),
    url(r'^finalize/$', 'finalize', name = 'finalize'),
    url(r'^review/(?P<project>\d+)$', 'review', name = 'review'),
    url(r'^review/submit/$', 'submit_review', name = 'review-submit'),
    url(r'^review/finalize/(?P<project>\d+)/$', 'finalize_review', name = 'review-finalize'),
    url(r'^asset/upload/$', 'upload_asset', name = 'upload_asset'),
    url(r'^assets/download/$', 'download_zip', name = 'download_zip'),
    url(r'^designer/$', 'designer', name = 'designer'),
    url(r'^designer/project/(?P<project>\d+)$', 'designer_project', name = 'designer_project'),
    url(r'^designer/submit/(?P<project>\d+)$', 'designer_submit', name = 'designer_submit'),
    url(r'^designer/create/$', 'create_designer', name = 'create_designer'),
    url(r'^designer/auth/$', 'auth_designer', name = 'auth_designer'),
    url(r'^designer/login/$', 'login_designer', name = 'login_designer'),
)

urlpatterns = patterns('',
    url(r'^$', 'src.controllers.index.index', name = 'index'),
    url(r'^', include(index_urlpatterns, namespace = 'index')),
    url(r'^user/', include(user_urlpatterns, namespace = 'user')),
    url(r'^payment/', include(payment_urlpatterns, namespace = 'payment')),
    url(r'^profile/', include(profile_urlpatterns, namespace = 'profile')),
    url(r'^lists/', include(list_urlpatterns, namespace = 'list')),
    url(r'^event/', include(event_urlpatterns, namespace = 'event')),
    url(r'^sponsorship/', 
        include(sponsorship_urlpatterns, namespace = 'sponsorship')),
    url(r'^bonus/', include(bonus_urlpatterns, namespace = 'bonus')), 
    url(r'^file/', include(file_urlpatterns, namespace = 'file')),
    url(r'^admin/', include(admin_urlpatterns, namespace = 'admin')),
    url(r'^designs/', include(designs_urlpatterns, namespace = 'designs')),
    url(r'^(?P<id>[A-Za-z0-9-]+)/$', 'src.controllers.event.index', name = 'event-slug'),
)

handler404 = 'src.controllers.index.pageNotFound'
handler500 = 'src.controllers.index.serverError'