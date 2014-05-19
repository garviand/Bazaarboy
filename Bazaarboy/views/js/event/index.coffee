Bazaarboy.event.index = 
    savingInProgress: false
    unsavedProgress: false
    toLaunch: false
    overlayAnimationInProgress: false
    redactorContent: undefined
    saveDescription: () ->
        scope = this
        description = $('div#event-description div.description div.inner').redactor('get')
        $('div.save-status').html 'Saving...'
        @savingInProgress = true
        Bazaarboy.post 'event/edit/', 
            id: eventId,
            description: description
        , (response) ->
            if response.status isnt 'OK'
                alert response.message
                $('div.event-launch a.launch-btn').html('Launch Event')
                $('div.save-status').html 'Saved'
                scope.toLaunch = false
            else
                @savingInProgress = false
                setTimeout (() ->
                    $('div.save-status').html 'Saved'
                    if scope.toLaunch
                        Bazaarboy.post 'event/launch/', {id: eventId}, (response) =>
                            if response.status is 'OK'
                                window.location = '/event/' + eventId + '#launch'
                            else
                                alert response.message
                                $('div.event-launch a.launch-btn').html('Launch Event')
                                scope.toLaunch = false
                            return
                    return
                ), 500
            return
        return
    updateSubtotal: () ->
        tickets = $('div#tickets-canvas div.ticket')
        totalPrice = 0
        totalQuantity = 0
        for ticket in tickets
            if $(ticket).find('input.ticket-selected').is ':checked'
                quantity = parseInt $(ticket).find('input.ticket-quantity').val()
                totalQuantity += quantity
                totalPrice += quantity * parseFloat $(ticket).attr('data-price')
        $('div#tickets-subtotal span.total').html totalPrice.toFixed(2)
        if totalPrice isnt 0
            $('div#tickets-subtotal span.fee').removeClass 'hide'
        else
            $('div#tickets-subtotal span.fee').addClass 'hide'
        $('div#tickets-subtotal span.count').html totalQuantity
        if totalQuantity is 1
            $('div#tickets-subtotal span.plural').addClass 'hide'
        else
            $('div#tickets-subtotal span.plural').removeClass 'hide'
        return
    purchase: () ->
        $('a#tickets-confirm').html 'Processing...'
        params = 
            event: eventId
            first_name: $('input[name=first_name]').val().trim()
            last_name: $('input[name=last_name]').val().trim()
            email: $('input[name=email]').val().trim()
            phone: $('input[name=phone]').val().trim()
            details: {}
        tickets = $('div#tickets-canvas div.ticket')
        for ticket in tickets
            if $(ticket).find('input.ticket-selected').is ':checked'
                quantity = parseInt $(ticket).find('input.ticket-quantity').val()
                params.details[$(ticket).attr('data-id')] = quantity
        params.details = JSON.stringify params.details
        if params.phone.length is 0
            delete params.phone
        console.log params
        Bazaarboy.post 'event/purchase/', params, (response) =>
            if response.status isnt 'OK'
                alert response.message
                $('a#tickets-confirm').html 'Confirm RSVP'
            else
                if not response.publishable_key?
                    @completePurchase(response.tickets)
                else
                    total = response.purchase.amount * 100
                    a = (1 + 0.05) * total + 50
                    b = (1 + 0.029) * total + 30 + 1000
                    total = Math.round(Math.min(a, b))
                    StripeCheckout.open
                        key: response.publishable_key
                        address: false
                        amount: total
                        currency: 'usd'
                        name: response.purchase.event.name
                        description: 'Tickets for ' + response.purchase.event.name
                        panelLabel: 'Checkout'
                        email: params.email
                        image: response.logo
                        token: (token) =>
                            Bazaarboy.post 'payment/charge/', 
                                checkout: response.purchase.checkout
                                stripe_token: token.id
                            , (response) =>
                                if response.status is 'OK'
                                    @completePurchase(response.tickets)
                                else
                                    alert response.message
                                return
                            return
            return
        return
    completePurchase: (tickets) ->
        scope = this
        if not @overlayAnimationInProgress
            @overlayAnimationInProgress = true
            ticketHTML = $('div#confirmation-modal div.ticket-model').html()
            $('div#confirmation-modal div.ticket-model').remove()
            for k, ticket of tickets
                newTicket = $(ticketHTML)
                newTicket.find('div.quantity').html('x'+ticket['quantity'])
                newTicket.find('div.name').html(ticket['name'])
                $('div#confirmation-modal').find('div.tickets').append(newTicket)
            $('div#wrapper-overlay').animate {opacity: 0}, 300, () ->
                $(this).addClass('hide')
                return
            $('div#tickets').animate {opacity: 0}, 300, () ->
                $(this).addClass('hide')
                scope.overlayAnimationInProgress = false
                return
        $('div#confirmation-modal').foundation('reveal', 'open')
        return
    search_organizers: () ->
        $('form.add-organizer-form div.organizer').remove()
        organizerModel = $('div.organizer-model')
        value = $('form.add-organizer-form input#organizer-name').val()
        Bazaarboy.get 'profile/search/', {keyword: value}, (response) =>
            if response.status is 'OK'
                profiles = response.profiles
                if profiles.length > 0
                    $('.profile_login .profile_choices').empty()
                    for i in [0..profiles.length-1]
                        newProfile = organizerModel
                        newProfile.find('div.organizer-name').html(profiles[i].name)
                        if profiles[i].image_url?
                            newProfile.find('div.organizer-image').html('<img src='+profiles[i].image_url+' />')
                        else
                            newProfile.find('div.organizer-image').html('&nbsp;')
                        newProfile.find('a.add-organizer-submit').attr('data-profile', profiles[i].pk)
                        $('form.add-organizer-form').append(newProfile.html())
            return
        return
    init: () ->
        scope = this
        $(window).hashchange () ->
            hash = location.hash
            if hash is '#launch'
                $('div#launch-modal').foundation('reveal', 'open')
                window.history.pushState("", document.title, window.location.pathname)
                return
            if hash is '#conf'
                $('div#confirmation-modal').foundation('reveal', 'open')
                return
        $(window).hashchange()
        # MOBILE HEADER FIX
        if $('div#event-header').height() > 66
            $('div#event-header').css('position', 'absolute')
            $('div#event').css('padding-top', $('div#event-header').height() + 'px')
            $('div#tickets').css('top', ($('div#event-header').height() + 20) + 'px')
        $(window).resize () ->
            if $('div#event-header').height() > 66
                $('div#event-header').css('position', 'absolute')
                $('div#tickets').css('top', ($('div#event-header').height() + 20) + 'px')
            else
                $('div#event-header').css('position', 'fixed')
                $('div#tickets').css('top', '100px')
            $('div#event').css('padding-top', $('div#event-header').height() + 'px')
            return
        latitude = parseFloat $('div.map-canvas').attr('data-latitude')
        longitude = parseFloat $('div.map-canvas').attr('data-longitude')
        if not isNaN(latitude) and not isNaN(longitude)
            # GET ADDRESS
            geocoder = new google.maps.Geocoder()
            latlng = new google.maps.LatLng(latitude, longitude)
            geocoder.geocode {'latLng': latlng}, (results, status) ->
                if results[0]
                    loc = results[0]['formatted_address'].split(",")
                    street = loc[0]
                    city_zip = loc[1] + ", " + loc[2]
                    $("div#event-location div.address span.street-address").html(street)
                    $("div#event-location div.address span.city-zip").html(city_zip)
                    $("div#event-location div.address").removeClass("hide")
                return 
            $('div.map-canvas').removeClass 'hide'
            mapCenter = new google.maps.LatLng latitude, longitude
            mapStyles = [
                featureType: 'poi'
                elementType: 'labels'
                stylers: [visibility: 'off']
            ]
            mapOptions =
                zoom: 15
                center: mapCenter
                draggable: false
                mapTypeControl: false
                scaleControl: false
                panControl: false
                scrollwheel: false
                streetViewControl: false
                zoomControl: false
                styles: mapStyles
            map = new google.maps.Map document.getElementById('map-canvas'), mapOptions
            marker = new google.maps.Marker
                position: mapCenter
                map: map
                url: "https://maps.google.com/?saddr=#{latitude},#{longitude}"
            google.maps.event.addListener marker, 'click', () ->
                window.open @url, '_blank'
                return
        if design
            $('div#event-description div.description div.inner').redactor
                buttons: [
                    'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                    'alignment', '|',
                    'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                    'horizontalrule', 'table', 'image', 'video', 'link', '|',
                    'html'
                ]
                boldTag: 'b'
                italicTag: 'i'
                imageUpload: rootUrl + 'file/image/upload/'
                toolbarFixedBox: true
            $('a.save.primary-btn').click () =>
                @saveDescription()
                return
            $('div.event-launch a.launch-btn').click () ->
                scope.toLaunch = true
                $('div.event-launch a.launch-btn').html('Launching...')
                scope.saveDescription()
                return
            $('div#event-description div.description div.inner').keyup () ->
                $('div.save-status').html 'Unsaved Changes'
                return
            scope.redactorContent = $('div#event-description div.description div.inner').redactor('get')
        $("div.event-share a.share-btn").click () ->
            $('div.event-rsvp, div.event-share, div.event-price').fadeOut 300, () ->
                $("div.event-share-canvas").fadeIn 300
                return
            return
        $("span.close-share").click () ->
            $("div.event-share-canvas").fadeOut 300, () ->
                $('div.event-rsvp, div.event-share, div.event-price').fadeIn 300
                return
            return
        $('a#rsvp-button').click () =>
            if not @overlayAnimationInProgress
                $("html, body").animate({ scrollTop: 0 }, "fast")
                if $('div#wrapper-overlay').hasClass('hide')
                    @overlayAnimationInProgress = true
                    $('div#wrapper-overlay').css('opacity', 0).removeClass('hide')
                    $('div#tickets').css('opacity', 0).removeClass('hide')
                    $('div#wrapper-overlay').animate {opacity: 1}, 300
                    $('div#tickets').animate {opacity: 1}, 300, () =>
                        @overlayAnimationInProgress = false
                        return
            return
        $('div#wrapper-overlay').click () =>
            if not @overlayAnimationInProgress
                @overlayAnimationInProgress = true
                $('div#wrapper-overlay').animate {opacity: 0}, 300, () ->
                    $(this).addClass('hide')
                    return
                $('div#tickets').animate {opacity: 0}, 300, () ->
                    $(this).addClass('hide')
                    scope.overlayAnimationInProgress = false
                    return
            return
        $('div#tickets-canvas div.ticket').click () ->
            $(this).find('.ticket-selected').click()
            return
        $('.ticket-selected').click (e) ->
            e.stopPropagation()
            return
        $('input.ticket-quantity').click (e) ->
            e.stopPropagation()
            return
        $('input.ticket-selected').click () ->
            wrapper = $(this).closest('div.wrapper')
            if $(this).is ':checked'
                if parseInt($(wrapper).find('input.ticket-quantity').val()) is 0
                    $(wrapper).find('input.ticket-quantity').val 1
            else
                $(wrapper).find('input.ticket-quantity').val 0
            scope.updateSubtotal()
            return
        $('input.ticket-quantity').keyup () ->
            wrapper = $(this).closest('div.wrapper')
            if $(this).val().trim() is '' or parseInt($(this).val()) is 0
                $(wrapper).find('input.ticket-selected').prop 'checked', false
            else
                $(wrapper).find('input.ticket-selected').prop 'checked', true
            scope.updateSubtotal()
            return
        $('input.ticket-quantity').blur () ->
            if $(this).val().trim() is ''
                $(this).val 0
            scope.updateSubtotal()
            return
        $('a#tickets-confirm').click () =>
            @purchase()
            return
        # CONTACT ORGANIZER
        $('a.contact-organizer-btn').click () ->
            $('div#contact-organizer-modal').foundation('reveal', 'open')
            return
        $('a.contact-organizer-close').click () ->
            $('div#contact-organizer-modal').foundation('reveal', 'close')
            return
        $('div.send-contact-organizer a.send-message').click () ->
            $(this).html('Sending...')
            $('form.contact-organizer-form').submit()
            return
        $('form.contact-organizer-form').submit (event) ->
            event.preventDefault()
            return
        $('form.contact-organizer-form').on 'valid', () ->
            params = $(this).serializeObject()
            optionals = []
            params = Bazaarboy.stripEmpty params, optionals
            console.log params
            Bazaarboy.post 'profile/message/', params, (response) ->
                if response.status is 'OK'
                    $('form.contact-organizer-form').fadeOut 300, () ->
                        $('div.row.contact-organizer-success').fadeIn 300
                        return
                else
                    alert response.message
                    $('div.send-contact-organizer a.send-message').html('Send Message')
            return
        # ADD ORGANIZER
        $('a.add-organizer-btn').click () ->
            $('div#add-organizer-modal').foundation('reveal', 'open')
            return
        $('a.add-organizer-close').click () ->
            $('div#add-organizer-modal').foundation('reveal', 'close')
            return
        $('a.add-organizer-another').click () ->
            $('div.row.add-organizer-success').fadeOut 300, () ->
                $('form.add-organizer-form').fadeIn 300
                return
            return
        add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers)
        $('form.add-organizer-form input#organizer-name').bind('keypress', add_organizer_debounce)
        $('form.add-organizer-form').on 'click', 'a.add-organizer-submit', () ->
            profileId = $(this).data('profile')
            Bazaarboy.post 'event/organizer/add/', {id: eventId, profile: profileId}, (response) =>
                if response.status is 'OK'
                    newOrganizer = $('div#event-organizers div.organizer').clone()
                    if response.profile['image_url']?
                        newOrganizer.find('div.organizer-icon').css("background-image", "url(#{response.profile.image_url})")
                    newOrganizer.find('div.organizer-name').html("<span>#{response.profile.name}</span>")
                    $('div#event-organizers div.organizer-list').append(newOrganizer)
                    console.log newOrganizer
                    $('form.add-organizer-form').fadeOut 300, () ->
                        $('form.add-organizer-form input#organizer-name').val('')
                        $('form.add-organizer-form div.organizer').remove()
                        $('div.row.add-organizer-success').fadeIn 300
                        return
                else
                    alert response.message
            return
        return

Bazaarboy.event.index.init()