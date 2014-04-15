Bazaarboy.event.index = 
    savingInProgress: false
    saveDescription: () ->
        description = $('div#event-description div.description div.inner').redactor('get')
        $('div.save-status').html 'Saving...'
        @savingInProgress = true
        Bazaarboy.post 'event/edit/', 
            id: eventId,
            description: description
        , (response) ->
            if response.status isnt 'OK'
                alert response.message
            else
                @savingInProgress = false
                setTimeout (() ->
                    $('div.save-status').html 'Saved'
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
            tickets: {}
        tickets = $('div#tickets-canvas div.ticket')
        for ticket in tickets
            if $(ticket).find('input.ticket-selected').is ':checked'
                quantity = parseInt $(ticket).find('input.ticket-quantity').val()
                params.tickets[$(ticket).attr('data-id')] = quantity
        Bazaarboy.post 'event/purchase/', params, (response) =>
            if response.status isnt 'OK'
                alert response.message
            else
                if not response.publishable_key?
                    @completePurchase()
                else
                    total = response.purchase.amount
                    a = (1 + 0.05) * total + 50
                    b = (1 + 0.029) * total + 30 + 1000
                    total = Math.round(Math.min(a, b))
                    StripeCheckout.open
                        key: response.publishable_key
                        address: false
                        amount: response.purchase.amount
                        currency: 'usd'
                        name: response.purchase.event.name
                        description: 'Tickets for ' + response.purchase.event.name
                        panelLabel: 'Checkout'
                        token: (token) =>
                            Bazaarboy.post 'payment/charge/', 
                                checkout: response.purchase.checkout
                                stripe_token: token
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
        return
    init: () ->
        scope = this
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
        return

Bazaarboy.event.index.init()