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
    url(r'^wepay/checkout/$', 'src.controllers.wepay.checkout', 
        name = 'wepay-checkout'),
    url(r'^wepay/preapproval/$', 'src.controllers.wepay.preapproval', 
        name = 'wepay-preapproval'),

    # City

    url(r'^city/(?P<id>\d+)/$', 'src.controllers.city.index', 
        name = 'city-index'),
    url(r'^city/$', 'src.controllers.city.city', name = 'city'),
    url(r'^city/create/$', 'src.controllers.city.create', 
        name = 'city-create'),
    url(r'^city/edit/$', 'src.controllers.city.edit', name = 'city-edit'),
    url(r'^city/delete/$', 'src.controllers.city.delete', 
        name = 'city-delete'),

    # Community

    url(r'^community/(?P<id>\d+)/$', 'src.controllers.community.index', 
        name = 'community-index'),
    url(r'^community/$', 'src.controllers.community.community', 
        name = 'community'),
    url(r'^community/create/$', 'src.controllers.community.create', 
        name = 'community-create'),
    url(r'^community/edit/$', 'src.controllers.community.edit', 
        name = 'community-edit'),
    url(r'^community/delete/$', 'src.controllers.community.delete', 
        name = 'community-delete'),

    # Profile

    url(r'^profile/(?P<id>\d+)/$', 'src.controllers.profile.index', 
        name = 'profile-index'),
    url(r'^profile/$', 'src.controllers.profile.profile', name = 'profile'),
    url(r'^profile/create/$', 'src.controllers.profile.create', 
        name = 'profile-create'),
    url(r'^profile/edit/$', 'src.controllers.profile.edit', 
        name = 'profile-edit'),
    url(r'^profile/delete/$', 'src.controllers.profile.delete', 
        name = 'profile-delete'),

    # Event

    url(r'^event/(?P<id>\d+)/$', 'src.controllers.event.index', 
        name = 'event-index'),
    url(r'^event/$', 'src.controllers.event.event', name = 'event'),
    url(r'^event/create/$', 'src.controllers.event.create', 
        name = 'event-create'),
    url(r'^event/edit/$', 'src.controllers.event.edit', name = 'event-edit'),
    url(r'^event/delete/$', 'src.controllers.event.delete', 
        name = 'event-delete'),
    url(r'^event/launch/$', 'src.controllers.event.launch', 
        name = 'event-launch'),
    url(r'^event/delaunch/$', 'src.controllers.event.delaunch', 
        name = 'event-delaunch'),
    url(r'^event/ticket/create/$', 'src.controllers.event.create_ticket', 
        name = 'event-ticket-create'),
    url(r'^event/ticket/edit/$', 'src.controllers.event.edit_ticket', 
        name = 'event-ticket-edit'),
    url(r'^event/ticket/delete/$', 'src.controllers.event.delete_ticket', 
        name = 'event-ticket-delete'),
    url(r'^event/purchase/$', 'src.controllers.event.purchase', 
        name = 'event-purchase'),

    # Initiative

    url(r'^initiative/(?P<id>\d+)/$', 'src.controllers.initiative.index', 
        name = 'initiative-index'),
    url(r'^initiative/$', 'src.controllers.initiative.initiative', 
        name = 'initiative'),
    url(r'^initiative/create/$', 'src.controllers.initiative.create', 
        name = 'initiative-create'),
    url(r'^initiative/edit/$', 'src.controllers.initiative.edit', 
        name = 'initiative-edit'),
    url(r'^initiative/delete/$', 'src.controllers.initiative.delete', 
        name = 'initiative-delete'),
    url(r'^initiative/launch/$', 'src.controllers.initiative.launch', 
        name = 'initiative-launch'),
    url(r'^initiative/delaunch/$', 'src.controllers.initiative.delaunch', 
        name = 'initiative-delaunch'),
    url(r'^initiative/reward/create/$', 
        'src.controllers.initiative.create_reward', 
        name = 'initiative-reward-create'),
    url(r'^initiative/reward/edit/$', 'src.controllers.initiative.edit_reward', 
        name = 'initiative-reward-edit'),
    url(r'^initiative/reward/delete/$', 
        'src.controllers.initiative.delete_reward', 
        name = 'initiative-reward-delete'),
    url(r'^initiative/pledge/$', 'src.controllers.initiative.pledge', 
        name = 'initiative-pledge'),

    # Fundraiser

    url(r'^fundraiser/(?P<id>\d+)/$', 'src.controllers.fundraiser.index', 
        name = 'fundraiser-index'),
    url(r'^fundraiser/$', 'src.controllers.fundraiser.fundraiser', 
        name = 'fundraiser'),
    url(r'^fundraiser/create/$', 'src.controllers.fundraiser.create', 
        name = 'fundraiser-create'),
    url(r'^fundraiser/edit/$', 'src.controllers.fundraiser.edit', 
        name = 'fundraiser-edit'),
    url(r'^fundraiser/delete/$', 'src.controllers.fundraiser.delete', 
        name = 'fundraiser-delete'),
    url(r'^fundraiser/launch/$', 'src.controllers.fundraiser.launch', 
        name = 'fundraiser-launch'),
    url(r'^fundraiser/delaunch/$', 'src.controllers.fundraiser.delaunch', 
        name = 'fundraiser-delaunch'),
    url(r'^fundraiser/donate/$', 'src.controllers.fundraiser.donate', 
        name = 'fundraiser-donate'),

)