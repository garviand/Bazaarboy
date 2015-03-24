Bazaarboy.event.index = 
    aviary: undefined
    savingInProgress: false
    unsavedProgress: false
    toLaunch: false
    overlayAnimationInProgress: false
    redactorContent: undefined
    emailSending: false
    requiresAddress: false
    currentCheckout: 'HI'
    ticketMenu: undefined
    ticketId: undefined
    purchasing: false
    DropDown: (el) ->
        this.dd = el
        this.placeholder = this.dd.children('span')
        this.opts = this.dd.find('ul.dropdown > li')
        this.val = ''
        this.index = -1
        this.ticket = undefined
        this.initEvents()
    saveDescription: () ->
        scope = this
        description = $('div#event-description div.description div.inner').redactor('code.get')
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
    stripeResponseHandler: (status, response, total) ->
        if status == 200
            swal
                title: "Confirm Purchase"
                text: "Ticket Price + Fees = $" + (total/100).toFixed(2)
                type: "success"
                showCancelButton: true
                confirmButtonText: "Purchase ($" + (total/100).toFixed(2) + ")"
                closeOnConfirm: true
                confirmButtonColor: "#1DBC85"
                , (isConfirm) =>
                    @purchasing = false
                    sendSms = $('input[name=phone]').val().trim() isnt ''
                    if isConfirm
                        Bazaarboy.post 'payment/charge/',
                            checkout: @currentCheckout
                            stripe_token: response.id
                            send_sms: sendSms
                            , (response) =>
                                console.log response
                                if response.status is 'OK'
                                    @completePurchase response.tickets
                                else
                                    alert response.message
                                    $('a#tickets-confirm').html 'Confirm RSVP'
                                return
                    else
                        $('a#tickets-confirm').html 'Confirm RSVP'
        else
            swal
                title: "Checkout Error"
                text: response.error.message
                type: "warning"
                , () ->
                    $('a#tickets-confirm').html 'Confirm RSVP'
                    return
        return
    purchase: () ->
        if not @purchasing
            @purchasing = true
            $('a#tickets-confirm').html 'Processing...'
            params = 
                event: eventId
                first_name: $('input[name=first_name]').val().trim()
                last_name: $('input[name=last_name]').val().trim()
                email: $('input[name=email]').val().trim()
                phone: $('input[name=phone]').val().trim()
                details: {}
            if $('input[name=invite_id]').val().trim() != ''
                params['invite'] = $('input[name=invite_id]').val()
            if @requiresAddress
                if $('input[name=address]').val().trim() == '' or $('input[name=state]').val().trim() == '' or $('input[name=city]').val().trim() == '' or $('input[name=zip]').val().trim() == ''
                    alert 'All Address Fields Are Required'
                    $('a#tickets-confirm').html 'Confirm RSVP'
                    @purchasing = false
                    return
            address = $('input[name=address]').val().trim()
            if $('input[name=city]').val().trim() != ''
                address += ', ' + $('input[name=city]').val().trim()
            if $('input[name=state]').val().trim() != ''
                address += ', ' + $('input[name=state]').val().trim()
            if $('input[name=zip]').val().trim() != ''
                address += ' ' + $('input[name=zip]').val().trim()
            params.address = address
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
                            if $(this).find('div.custom-option.active').length > 0
                                params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = $(this).find('div.custom-option.active').data('option')
                            return
                    if $(ticket).find('div.custom-field-group').length > 0
                        fields = $(ticket).find('div.custom-field-group')
                        $.each fields, (target) ->
                            fieldValue = $(this).find('input.custom-field-input').val()
                            if String(fieldValue).trim() isnt ''
                                params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = String(fieldValue).trim()
                            else
                                params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = ' '
            params.details = JSON.stringify params.details
            console.log $('.cc-number').val() is ''
            console.log $('.cc-number').val()
            if params.phone.length is 0
                delete params.phone
            if not ticketSelected
                alert 'You Must Select A Ticket'
                $('a#tickets-confirm').html 'Confirm RSVP'
                @purchasing = false
                return
            else if params.first_name is ''
                alert 'Please Add a First Name'
                $('a#tickets-confirm').html 'Confirm RSVP'
                @purchasing = false
                return
            else if params.last_name is ''
                alert 'Please Add a Last Name'
                $('a#tickets-confirm').html 'Confirm RSVP'
                @purchasing = false
                return
            else if params.email is ''
                alert 'Please Add an Email'
                $('a#tickets-confirm').html 'Confirm RSVP'
                @purchasing = false
                return 
            else
                Bazaarboy.post 'event/purchase/', params, (response) =>
                    if response.status isnt 'OK'
                        alert response.message
                        $('a#tickets-confirm').html 'Confirm RSVP'
                        @purchasing = false
                    else
                        if not response.publishable_key?
                            @completePurchase(response.tickets)
                            @purchasing = false
                        else
                            total = response.purchase.amount * 100
                            a = (1 + 0.05) * total + 50
                            b = (1 + 0.029) * total + 30 + 1000
                            total = Math.round(Math.min(a, b))
                            @currentCheckout = response.purchase.checkout
                            Stripe.setPublishableKey response.publishable_key
                            paymentInfo =
                                number: $('.cc-number').val().replace(/\ /g, '')
                                cvc: $('.cc-cvc').val()
                                exp_month: $('.cc-exp').val().split('/')[0].trim()
                                exp_year: $('.cc-exp').val().split('/')[1].trim()
                            Stripe.card.createToken paymentInfo, (status, response) =>
                                @stripeResponseHandler status, response, total
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
            $('input[name=state]').val('')
            $('input[name=city]').val('')
            $('input[name=zip]').val('')
            $('input.ticket-selected').prop('checked', false)
            $('div#confirmation-modal').foundation('reveal', 'open')
        return
    init: () ->
        scope = this
        $('.cc-exp').payment('formatCardExpiry');
        $('.cc-number').payment('formatCardNumber');
        $('.cc-cvc').payment('formatCardCVC');
        $('input.cc-number').keypress () ->
            if $(this).hasClass('visa')
                $('div.credit-cards img').css('opacity', '.1')
                $('img.visa-img').css('opacity', '1')
            else if $(this).hasClass('mastercard')
                $('div.credit-cards img').css('opacity', '.1')
                $('img.mastercard-img').css('opacity', '1')
            else if $(this).hasClass('discover')
                $('div.credit-cards img').css('opacity', '.1')
                $('img.discover-img').css('opacity', '1')
            else if $(this).hasClass('amex')
                $('div.credit-cards img').css('opacity', '.1')
                $('img.americanexpress-img').css('opacity', '1')
            else
                $('div.credit-cards').css('opacity', '1')
            return
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
        $('iframe#ticket-embed-iframe').load () ->
            oldEmbed = $('textarea.embed-code').html()
            newHeight = this.contentWindow.document.body.scrollHeight + 130
            newEmbed = oldEmbed.replace("[IFRAME_HEIGHT]", newHeight);
            $('textarea.embed-code').html newEmbed
            $('iframe#ticket-embed-iframe').css('height', newHeight + 'px')
            return
        if $('.tix-type').length == 1
            scope.ticketId = $('.tix-type').data('id')
        @DropDown:: =
            initEvents: ->
                obj = this
                obj.dd.on "click", (event) ->
                    $(this).toggleClass "active"
                    false
                    return
                obj.opts.on "click", ->
                    opt = $(this)
                    obj.val = opt.text()
                    obj.index = opt.index()
                    obj.placeholder.text obj.val
                    scope.ticketId = opt.find('a').data('id')
                    $("form.hero-ticket-form button[type=submit]").click()
                    return
                return
            getValue: ->
                @val
                return
            getIndex: ->
                @index
                return
        @ticketMenu = new @DropDown($('#dd'))
        $("form.hero-ticket-form button[type=submit], .tix-type").click (e) ->
            e.preventDefault()
            ticketId = scope.ticketId
            if not $("div#tickets div.ticket[data-id=" + ticketId + "]").hasClass('active')
                $("div#tickets div.ticket[data-id=" + ticketId + "] div.ticket-top").click()
            if not Bazaarboy.event.index.overlayAnimationInProgress
                $("html, body").animate({ scrollTop: 0 }, "fast")
                if $('div#wrapper-overlay').hasClass('hide')
                    Bazaarboy.event.index.overlayAnimationInProgress = true
                    $('div#wrapper-overlay').css('opacity', 0).removeClass('hide')
                    $('div#tickets').css('opacity', 0).removeClass('hide')
                    $('div#wrapper-overlay').animate {opacity: 1}, 300
                    $('div#tickets').animate {opacity: 1}, 300, () =>
                        Bazaarboy.event.index.overlayAnimationInProgress = false
                        return
        $('div.custom-option-group div.custom-option').click () ->
            $(this).parents('div.custom-option-group').find('div.custom-option').removeClass 'active'
            $(this).addClass 'active'
            return
        # MOBILE HEADER FIX
        if $('div#event-header').height() > 66 and not design
            $('div#event-header').css('position', 'absolute')
            $('div#event').css('padding-top', $('div#event-header').height() + 'px')
            $('div#tickets').css('top', ($('div#event-header').height() + 20) + 'px')
        $(window).resize () ->
            if $('div#event-header').height() > 66
                $('div#event-header').css('position', 'absolute')
                $('div#tickets').css('top', ($('div#event-header').height() + 20) + 'px')
            else
                if not design
                    $('div#event-header').css('position', 'fixed')
                    $('div#tickets').css('top', '100px')
            $('div#event').css('padding-top', $('div#event-header').height() + 'px')
            return
        # INVITE MODAL INIT
        $('div#invite-modal form.invite-form div.event-list').click () ->
            $(this).toggleClass 'selected'
            return
        $('div#invite-modal form.invite-form a.send-invitation').click () ->
            $(this).html 'Sending Email...'
            params = $('form.invite-form').serializeObject()
            events = ''
            $('div#invite-modal form.invite-form div.event-list.selected').each () ->
                if events isnt ''
                    events += ','
                events += $(this).data('id')
                return
            params['events'] = events
            optionals = ['emails', 'events', 'inviter', 'message', 'subject']
            params = Bazaarboy.stripEmpty params, optionals
            if not scope.emailSending
                scope.emailSending = true
                $('div#invite-modal form.invite-form a.send-invitation').addClass 'disabled-btn'
                Bazaarboy.post 'event/'+eventId+'/manualinvite/', params, (response) ->
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
                        $('div#invite-modal form.invite-form a.send-invitation').removeClass 'disabled-btn'
                    return
            return
        $('a.embed-code-btn').click () ->
            $('div#embed-code-modal').foundation('reveal', 'open')
            return
        $('a.embed-code-close').click () ->
            $('div#embed-code-modal').foundation('reveal', 'close')
            return
        $('.close-invite-modal').click () ->
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
            currentHTML = $('div#event-description div.description div.inner').html()
            redactorContent = $('div#event-description div.description div.inner').redactor
                plugins: ['instagram', 'video']
                boldTag: 'b'
                italicTag: 'i'
                imageUpload: rootUrl + 'file/image/upload/'
                toolbarFixedBox: true
                placeholder: 'Add Your Event Description Here...'
            $('a.save.secondary-btn').click () =>
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
            scope.redactorContent = $('div#event-description div.description div.inner').redactor('code.get')
            # Cover image
            $('form.upload_cover a.upload_cover_btn').click () ->
                $('form.upload_cover input[name=image_file]').click()
                return
            $('form.upload_cover a.delete_cover_btn').click () ->
                if confirm 'Are you sure you want to delete your cover image?'
                    Bazaarboy.post 'event/edit/', 
                        id: eventId,
                        cover: 'delete'
                    , (response) ->
                        if response.status is 'OK'
                            $('img#cover-image').attr 'src', ''
                            $('form.upload_cover a.delete_cover_btn').addClass 'hidden'
                            $('form.upload_cover a.upload_cover_btn').removeClass 'hidden'
                            $('div#event-hero').addClass 'hide'
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
                    $("img#cover-image").attr 'src', imageUrl
                    @aviary.close();
                    $('form.upload_cover a.upload_cover_btn').html 'Saving...'
                    Bazaarboy.post 'file/aviary/', 
                        event: eventId,
                        url: imageUrl
                    , (response) ->
                        $('form.upload_cover a.upload_cover_btn').addClass 'hidden'
                        $('form.upload_cover a.upload_cover_btn').html 'Upload Cover Image'
                        $('form.upload_cover a.delete_cover_btn').removeClass 'hidden'
                        $('img#cover-image').attr 'src', response.image
                        $('div#event-hero').css('background-image', 'url(' + imageUrl + ')')
                        $('div#event-hero').removeClass 'hide'
                        return
                    return
            $('form.upload_cover input[name=image_file]').fileupload
                url: rootUrl + 'file/image/upload/'
                type: 'POST'
                add: (event, data) =>
                    data.submit()
                    return
                done: (event, data) =>
                    response = jQuery.parseJSON data.result
                    if response.status is 'OK'
                        $('img#cover-image').attr 'src', mediaUrl + response.image.source
                        @aviary.launch
                            image: 'cover-image'
                            url: mediaUrl + response.image.source
                            maxSize: 1160
                            #cropPresets: ['1000x400']
                            #cropPresetsStrict: true
                            #forceCropPreset: ['Cover Image Size','10:4']
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
        $('div#tickets-canvas div.ticket.invalid div.ticket-top').hover ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('div.ticket').find('.timing-container').addClass 'underline'
            return
        , ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('div.ticket').find('.timing-container').removeClass 'underline'
            return
        $('div#tickets-canvas div.ticket.valid div.ticket-top').hover ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('div.ticket').addClass 'hover'
            return
        , ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('div.ticket').removeClass 'hover'
            return
        $('div#tickets-canvas div.ticket.valid div.ticket-top').click () ->
            if not $(this).parents('div.ticket').hasClass 'soldout'
                $(this).parents('.ticket').toggleClass 'active'
                if $(this).parents('.ticket').hasClass('active')
                    $(this).parents('.ticket').find('div.ticket-middle').slideDown 100
                    quant = $(this).parents('.ticket').find('input.ticket-quantity')
                    if quant.val().trim() is '' or parseInt(quant.val()) is 0
                        quant.val 1
                else
                    $(this).parents('.ticket').find('div.ticket-middle').slideUp 100
                $('.address-container').addClass 'hide'
                $('form#payment-form').addClass 'hide'
                $('a#tickets-confirm').html 'Confirm RSVP'
                scope.requiresAddress = false
                $('div.ticket').each () ->
                    if $(this).data('address') == 'yes' and $(this).hasClass('active')
                        $('.address-container').removeClass 'hide'
                        scope.requiresAddress = true
                    if parseInt($(this).data('price')) != 0 and $(this).hasClass('active')
                        $('form#payment-form').removeClass 'hide'
                        $('a#tickets-confirm').html 'Purchase'
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
        $("span.email-invite").click (e) ->
            $('div#invite-modal').foundation('reveal', 'open')
            $('div#invite-modal div.previous-events').addClass 'hide'
            $('div#invite-modal div.inviter').removeClass 'hide'
            return
        return

Bazaarboy.event.index.init()