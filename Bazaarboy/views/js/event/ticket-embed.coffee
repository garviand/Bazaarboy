Bazaarboy.event.ticket_embed =
    requiresAddress: false
    currentCheckout: 'HI'
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
    stripeResponseHandler: (status, response) ->
        if status == 200
            Bazaarboy.post 'payment/charge/', 
                checkout: @currentCheckout
                stripe_token: response.id
                , (response) =>
                    if response.status is 'OK'
                        @completePurchase response.tickets
                    else
                        alert response.message
                        $('a#tickets-confirm').html 'Confirm RSVP'
                    return
        else
            console.log response
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
        if @requiresAddress
            if $('input[name=address]').val().trim() == '' or $('input[name=state]').val().trim() == '' or $('input[name=city]').val().trim() == '' or $('input[name=zip]').val().trim() == ''
                alert 'All Address Fields Are Required'
                $('a#tickets-confirm').html 'Confirm RSVP'
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
                        ###
                        @currentCheckout = response.purchase.checkout
                        Stripe.setPublishableKey response.publishable_key
                        Stripe.card.createToken $("form#payment-form"), (status, response) =>
                            @stripeResponseHandler status, response
                            return
                        ###
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
        if $('.tix-type').length == 1
            scope.ticketId = $('.tix-type').data('id')
        $('div.custom-option-group div.custom-option').click () ->
            $(this).parents('div.custom-option-group').find('div.custom-option').removeClass 'active'
            $(this).addClass 'active'
            return
        # PROMOS
        $('div#tickets-details a.start-promo-btn').click () ->
            $('div.start-promo').fadeOut 300, () ->
                $('div.enter-promo').fadeIn 300
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
                $('.payment-container').addClass 'hide'
                scope.requiresAddress = false
                $('div.ticket').each () ->
                    if $(this).data('address') == 'yes' and $(this).hasClass('active')
                        $('.address-container').removeClass 'hide'
                        scope.requiresAddress = true
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
        return

Bazaarboy.event.ticket_embed.init()