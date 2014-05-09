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
        Bazaarboy.post 'event/purchase/', params, (response) =>
            if response.status isnt 'OK'
                alert response.message
            else
                if not response.publishable_key?
                    @completePurchase()
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
                                    @completePurchase()
                                else
                                    alert response.message
                                return
                            return
            return
        return
    completePurchase: () ->
        scope = this
        if not @overlayAnimationInProgress
            @overlayAnimationInProgress = true
            $('div#wrapper-overlay').animate {opacity: 0}, 300, () ->
                $(this).addClass('hide')
                return
            $('div#tickets').animate {opacity: 0}, 300, () ->
                $(this).addClass('hide')
                scope.overlayAnimationInProgress = false
                return
        $('div#confirmation-modal').foundation('reveal', 'open')
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
        latitude = parseFloat $('div.map-canvas').attr('data-latitude')
        longitude = parseFloat $('div.map-canvas').attr('data-longitude')
        if latitude isnt NaN and longitude isnt NaN
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
            $('a.save.primary-btn').click () =>
                @saveDescription()
                return
            $('div.event-launch a.launch-btn').click () ->
                scope.toLaunch = true
                $('div.event-launch a.launch-btn').html('Launching...')
                scope.saveDescription()
                return
            $('div#event-description div.description div.inner').keyup () ->
                $('div.save-status').html 'Editing'
                return
            scope.redactorContent = $('div#event-description div.description div.inner').redactor('get')
            # SET AUTO SAVE TIMER
            setInterval (() =>
                if $('div#event-description div.description div.inner').redactor('get') != scope.redactorContent
                    scope.redactorContent = $('div#event-description div.description div.inner').redactor('get')
                    scope.saveDescription()
                return
            ), 5000
        $("div#event-actions a.share-btn").click () ->
            $('div#event-actions').fadeOut 300, () ->
                $("div.share-canvas").fadeIn 300
                return
            return
        $("span.close-share").click () ->
            $("div.share-canvas").fadeOut 300, () ->
                $("div#event-actions").fadeIn 300
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
        return

Bazaarboy.event.index.init()