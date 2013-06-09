from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^$', 'kernel.src.controllers.landing.index', 
        name='Bazaarboy-Landing'),

)