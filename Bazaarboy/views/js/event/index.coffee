Bazaarboy.event.index = 
    aviary: undefined
    savingInProgress: false
    unsavedProgress: false
    toLaunch: false
    overlayAnimationInProgress: false
    redactorContent: undefined
    emailSending: false
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
                                window.location = eventUrl + '#launch'
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
        tickets = $('div#tickets-canvas div.ticket.active')
        totalPrice = 0
        totalQuantity = 0
        for ticket in tickets
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
            address: $('input[name=address]').val().trim()
            details: {}
        if $('input[name=promos]').length > 0
            if $('input[name=promos]').val().trim() isnt ''
                params['promos'] = $('input[name=promos]').val().trim()
        tickets = $('div#tickets-canvas div.ticket')
        ticketSelected = false
        for ticket in tickets
            if $(ticket).hasClass('active')
                ticketSelected = true
                quantity = parseInt $(ticket).find('input.ticket-quantity').val()
                params.details[$(ticket).attr('data-id')] = {'quantity':quantity, 'extra_fields': {}}
                if $(ticket).find('div.custom-option-group').length > 0
                    options = $(ticket).find('div.custom-option-group')
                    $.each options, (target) ->
                        if $(this).find('a.custom-option.active').length > 0
                            params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = $(this).find('a.custom-option.active').data('option')
                        return
                if $(ticket).find('div.custom-field-group').length > 0
                    fields = $(ticket).find('div.custom-field-group')
                    $.each fields, (target) ->
                        fieldValue = $(this).find('input.custom-field-input').val()
                        if String(fieldValue).trim() isnt ''
                            params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = String(fieldValue).trim()
                        return
        params.details = JSON.stringify params.details
        console.log params.details
        if params.phone.length is 0
            delete params.phone
        if not ticketSelected
            alert 'You Must Select A Ticket'
            $('a#tickets-confirm').html 'Confirm RSVP'
        else if params.first_name is ''
            alert 'Please Add a First Name'
            $('a#tickets-confirm').html 'Confirm RSVP'
            return
        else if params.last_name is ''
            alert 'Please Add a Last Name'
            $('a#tickets-confirm').html 'Confirm RSVP'
            return
        else if params.email is ''
            alert 'Please Add an Email'
            $('a#tickets-confirm').html 'Confirm RSVP'
            return
        else
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
                            closed: () ->
                                $('a#tickets-confirm').html 'Confirm RSVP'
                                return
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
            $('div#confirmation-modal div.ticket').hide()
            ticketHTML = $('div#confirmation-modal div.ticket-model').html()
            for k, ticket of tickets
                newTicket = $(ticketHTML)
                newTicket.find('div.quantity').html('x'+ticket['quantity'])
                newTicket.find('div.name').html(ticket['name'])
                $('div#confirmation-modal').find('div.tickets').append(newTicket)
                newTicket.show()
            $('div#wrapper-overlay').animate {opacity: 0}, 300, () ->
                $(this).addClass('hide')
                return
            $('div#tickets').animate {opacity: 0}, 300, () ->
                $(this).addClass('hide')
                scope.overlayAnimationInProgress = false
                return
            $('.ticket').find('div.ticket-middle').slideUp 100
            $('.ticket.active').removeClass 'active'
            $('a#tickets-confirm').html 'Confirm RSVP'
            $('input[name=quantity]').val(0)
            $('input[name=first_name]').val('')
            $('input[name=last_name]').val('')
            $('input[name=email]').val('')
            $('input[name=phone]').val('')
            $('input[name=address]').val('')
            $('input.ticket-selected').prop('checked', false)
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
            if hash is '#invite'
                $('div#invite-modal').foundation('reveal', 'open')
                window.history.pushState("", document.title, window.location.pathname)
                return
            if hash is '#conf'
                $('div#confirmation-modal').foundation('reveal', 'open')
                return
        $(window).hashchange()
        $('div.custom-option-group a.custom-option').click () ->
            $(this).parents('div.custom-option-group').find('a.custom-option').removeClass 'active'
            $(this).addClass 'active'
            return
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
        # LAUNCH MODAL
        $('div#launch-modal a.start-invite').click () ->
            $('div#invite-modal').foundation('reveal', 'open')
            return
        # INVITE MODAL INIT
        $('div#invite-modal form.invite-form div.event-list').click () ->
            $(this).toggleClass 'selected'
            return
        $('div#invite-modal form.invite-form a.send-invitation').click () ->
            $(this).html 'Sending...'
            params = $('form.invite-form').serializeObject()
            events = ''
            $('div#invite-modal form.invite-form div.event-list.selected').each () ->
                if events isnt ''
                    events += ','
                events += $(this).data('id')
                return
            params['events'] = events
            optionals = ['emails', 'events']
            params = Bazaarboy.stripEmpty params, optionals
            if not scope.emailSending
                scope.emailSending = true
                Bazaarboy.post 'event/'+eventId+'/invite/', params, (response) ->
                    if response.status is 'OK'
                        $('div.invite-success span.invite-count').html(response.count)
                        $('form.invite-form').fadeOut 300, () ->
                            scope.emailSending = false
                            $('div.invite-success').fadeIn 300
                            return
                    else
                        scope.emailSending = false
                        alert response.message
                        $(this).html 'Send Invitations'
                    return
            return
        $('div.invite-success a.close-invite-modal').click () ->
            $('div#invite-modal').foundation('reveal', 'close')
            return
        # PROMOS
        $('div#tickets-details a.start-promo-btn').click () ->
            $('div.start-promo').fadeOut 300, () ->
                $('div.enter-promo').fadeIn 300
                return
        # ADD THIS EVENT INIT
        addthisevent.settings
            outlook   : {show:true, text:"Outlook Calendar"}
            google    : {show:true, text:"Google Calendar"}
            yahoo     : {show:true, text:"Yahoo Calendar"}
            hotmail   : {show:false, text:"Hotmail Calendar"}
            ical      : {show:true, text:"iCal Calendar"}
            facebook  : {show:true, text:"Facebook Event"}
            dropdown  : {order:"google,ical,outlook,yahoo,hotmail"}
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
                {
                    featureType: "administrative"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "on"
                        }
                        {
                            saturation: -100
                        }
                        {
                            lightness: 20
                        }
                    ]
                }
                {
                    featureType: "road"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "on"
                        }
                        {
                            saturation: -100
                        }
                        {
                            lightness: 40
                        }
                    ]
                }
                {
                    featureType: "water"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "on"
                        }
                        {
                            saturation: -10
                        }
                        {
                            lightness: 30
                        }
                    ]
                }
                {
                    featureType: "landscape.man_made"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "simplified"
                        }
                        {
                            saturation: -60
                        }
                        {
                            lightness: 10
                        }
                    ]
                }
                {
                    featureType: "landscape.natural"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "simplified"
                        }
                        {
                            saturation: -60
                        }
                        {
                            lightness: 60
                        }
                    ]
                }
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
            iconImage =
                url: staticUrl + "images/map_icon.png"
                size: new google.maps.Size(200, 111)
                origin: new google.maps.Point(0, 15)
                anchor: new google.maps.Point(100, 55)
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
                placeholder: 'Add Your Event Description Here...'
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
            # Cover image
            $('div#event-cover form.upload_cover a.upload_cover_btn').click () ->
                $('div#event-cover form.upload_cover input[name=image_file]').click()
                return
            $('div#event-cover form.upload_cover a.edit_cover_btn').click () ->
                scope.aviary.launch
                    image: 'cover-image'
                    url: $("#cover-image").attr('src')
                return
            $('div#event-cover form.upload_cover a.delete_cover_btn').click () ->
                if confirm 'Are you sure you want to delete your cover image?'
                    Bazaarboy.post 'event/edit/', 
                        id: eventId,
                        cover: 'delete'
                    , (response) ->
                        if response.status is 'OK'
                            $('img#cover-image').attr 'src', ''
                            $('div#event-cover form.upload_cover a.delete_cover_btn').addClass 'hidden'
                            $('div#event-cover form.upload_cover a.edit_cover_btn').addClass 'hidden'
                            $('div#event-cover form.upload_cover a.upload_cover_btn').removeClass 'hidden'
                        else
                            alert response.message
                        return
                return
            postData = 
                event: eventId
            @aviary = new Aviary.Feather
                apiKey: 'ce3b87fb1edaa22c'
                apiVersion: 3
                enableCORS: true
                onSave: (imageId, imageUrl) =>
                    $("img##{imageId}").attr 'src', imageUrl
                    @aviary.close();
                    $('div#event-cover form.upload_cover a.delete_cover_btn').removeClass 'hidden'
                    $('div#event-cover form.upload_cover a.edit_cover_btn').removeClass 'hidden'
                    $('div#event-cover form.upload_cover a.upload_cover_btn').addClass 'hidden'
                    Bazaarboy.post 'file/aviary/', 
                        event: eventId,
                        url: imageUrl
                    , (response) ->
                        $('img#cover-image').attr 'src', response.image
                        return
                    return
            $('div#event-cover form.upload_cover input[name=image_file]').fileupload
                url: rootUrl + 'file/image/upload/'
                type: 'POST'
                add: (event, data) =>
                    data.submit()
                    return
                done: (event, data) =>
                    response = jQuery.parseJSON data.result
                    if response.status is 'OK'
                        $('img#cover-image-placeholder').attr 'src', mediaUrl + response.image.source
                        $('img#cover-image').attr 'src', mediaUrl + response.image.source
                        @aviary.launch
                            image: 'cover-image-placeholder'
                            url: mediaUrl + response.image.source
                    else
                        alert response.message
                    return
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
        $('div#tickets-canvas div.ticket div.ticket-top').hover ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('div.ticket').addClass 'hover'
            return
        , ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('div.ticket').removeClass 'hover'
            return
        $('div#tickets-canvas div.ticket-top').click () ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('.ticket').toggleClass 'active'
                if $(this).parents('.ticket').hasClass('active')
                    $(this).parents('.ticket').find('div.ticket-middle').slideDown 100
                    quant = $(this).parents('.ticket').find('input.ticket-quantity')
                    if quant.val().trim() is '' or parseInt(quant.val()) is 0
                        quant.val 1
                else
                    $(this).parents('.ticket').find('div.ticket-middle').slideUp 100
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
            if $(this).val().trim() is '' or parseInt($(this).val()) is 0
                $(this).val 0
                $(this).parents('.ticket').removeClass 'active'
                $(this).parents('.ticket').find('div.ticket-middle').slideUp 100
            scope.updateSubtotal()
            return
        $('a#tickets-confirm').click () =>
            @purchase()
            return
        # SEND RSVP ISSUE
        $('a.issue-btn').click () ->
            $('div#issue-modal').foundation('reveal', 'open')
            return
        $('a.issue-close').click () ->
            $('div#issue-modal').foundation('reveal', 'close')
            return
        $('div.send-issue a.send-issue-btn').click () ->
            $(this).html('Sending...')
            $('form.issue-form').submit()
            return
        $('form.issue-form').submit (event) ->
            event.preventDefault()
            return
        $('form.issue-form').on 'valid', () ->
            params = $(this).serializeObject()
            optionals = []
            params = Bazaarboy.stripEmpty params, optionals
            console.log params
            Bazaarboy.post 'event/issue/', params, (response) ->
                if response.status is 'OK'
                    $('form.issue-form').fadeOut 300, () ->
                        $('div.row.issue-success').fadeIn 300
                        return
                else
                    alert response.message
                    $('div.send-issue a.send-message').html('Send Message')
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
                    newOrganizer = $('div#event-organizers div.organizer').eq(0).clone()
                    if response.profile['image_url']?
                        newOrganizer.find('div.organizer-icon').css("background-image", "url(#{response.profile.image_url})")
                    else
                        newOrganizer.find('div.organizer-icon').css("background-image", "none")
                    newOrganizer.find('div.organizer-name').html("<span>#{response.profile.name}</span>")
                    $('div#event-organizers div.organizer-list').append(newOrganizer)
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