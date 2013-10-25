Bazaarboy.index.index = 
    adjustOverlayHeight: () ->
        height = 0
        for i in [0...$('div.overlay_canvas > div').not('div.hidden').length]
            height += $($('div.overlay_canvas > div')
                            .not('div.hidden')[i])
                            .outerHeight(true)
        $('div.overlay_canvas').height(height)
        return
    createEvent: (profileId) ->
        Bazaarboy.post 'event/create/', {profile: profileId}, (response) =>
            if response.status is 'OK'
                Bazaarboy.redirect 'event/' + response.event.pk + '/'
            else
                alert response.message
            return
        return
    savePaymentConnectSettings: () ->
        promises = []
        $('div#connect div.profiles form').each () ->
            params = $(this).serializeObject()
            if parseInt(params.payment) > 0
                promise = Bazaarboy.post 'profile/edit/', params, (response) ->
                    if response.status isnt 'OK'
                        alert response.message
                    return
                promises.push promise
            return
        $.when.apply($, promises).done () ->
            window.location.href = window.location.href.split('#')[0]
            return
        return
    showPaymentConnectOverlay: () ->
        $('div#wrapper_overlay').addClass('show').fadeIn(200)
        $('div#connect').fadeIn 200, () =>
            @adjustOverlayHeight()
        return
    init: () ->
        scope = this
        # Create event
        $('div#index div.profile div.header div.create a').click () ->
            profileId = $(this).parent().find('span.profile_id').html()
            scope.createEvent profileId
            return
        # Stripe connect
        $('div#index div.profiles div.profile div.summary a.connect').click () =>
            if $('div#connect').length is 0
                window.location.href = stripeConnectUrl
            else
                @showPaymentConnectOverlay()
            return
        # Overlay
        $('div#wrapper_overlay').click () ->
            if not $(this).hasClass('show')
                $('div#wrapper_overlay').fadeOut(200)
                $('div.overlay_canvas').fadeOut(200)
            return
        # Connect stripe with profile
        $('div#connect div.actions a.save').click () =>
            @savePaymentConnectSettings()
            return
        if window.location.hash? and window.location.hash is '#connect'
            @showPaymentConnectOverlay()
        return

Bazaarboy.index.index.init()