Bazaarboy.event.manage =
    selectionStatus: 'all'
    checkinStatus: 'all'
    purchaseInProgress: false
    add_purchase: () ->
        @purchaseInProgress = true
        $('div#rsvp div.action a.confirm').css('display', 'none')
        $('div#rsvp div.action div.loading').removeClass('hide')
        params = 
            event: eventId
            first_name: $('form[name=add-guest] input[name=first_name]').val().trim()
            last_name: $('form[name=add-guest] input[name=last_name]').val().trim()
            email: $('form[name=add-guest] input[name=email]').val().trim()
            details: {}
        ticketId = parseInt($('form[name=add-guest] select[name=ticket]').val())
        params.details[ticketId] = parseInt($('form[name=add-guest] input[name=quantity]').val())
        params.details = JSON.stringify params.details
        $('form[name=add-guest] input[name=submit]').val('Adding...')
        Bazaarboy.post 'event/purchase/add/', params, (response) =>
            if response.status is 'OK'
                $('form[name=add-guest] input[name=first_name]').val('')
                $('form[name=add-guest] input[name=last_name]').val('')
                $('form[name=add-guest] input[name=email]').val('')
                $('form[name=add-guest] input[name=quantity]').val('')
                $('form[name=add-guest] input[name=submit]').val('Add Guest(s)')
                newGuest = $('div.guest_template').clone()
                newGuest.find('div.confirmation').html(response.purchase.code + '&nbsp;')
                newGuest.find('div.ticket_name').html(response.tickets[ticketId]['name'] + ' (' + response.tickets[ticketId]['quantity'] + ')')
                newGuest.find('div.name').html(params.first_name + ' ' + params.last_name)
                newGuest.data('id', response.purchase.id)
                newGuest.data('ticket', ticketId)
                newGuest.removeClass('guest_template').removeClass('hidden')
                $('div.list_headers').after(newGuest)
                @purchaseInProgress = false
            else
                alert response.message
                @purchaseInProgress = false
            return
        return
    checkin: (guest_id) =>
        Bazaarboy.post 'event/checkin/', {id:guest_id}, (response) =>
            return
        return
    checkout: (guest_id) =>
        Bazaarboy.post 'event/checkin/', {id:guest_id, cancel:true}, (response) =>
            return
        return
    filterGuests: (param, value, ticketType, checkStatus, updateListLength) ->
        length = $('div.guest').length
        for i in [0..length-1]
            rsvp = $('div.guest:eq(' + i + ')')
            targetValue = $(rsvp).find('div.' + param).html()
            if targetValue.toLowerCase().indexOf(value.toLowerCase()) != -1
                if String(rsvp.data('ticket')).indexOf(',') > -1
                    ticketCheck = $.inArray(String(ticketType), String(rsvp.data('ticket')).split(',')) > -1
                else
                    ticketCheck = rsvp.data('ticket') == ticketType
                if ticketCheck or ticketType == 'all'
                    $(rsvp).removeClass('hide')
            if(checkStatus == 'checked_in')
                if not $(rsvp).hasClass('checked_in')
                    $(rsvp).addClass('hide')
            if(checkStatus == 'not_checked_in')
                if $(rsvp).hasClass('checked_in')
                    $(rsvp).addClass('hide')
        if updateListLength
            newLength = $('div.guest').not('.hide').length
            newLengthChecked = $('div.guest.checked_in').not('.hide').length
            $('div.checkin_numbers span.total_guests').html(newLength)
            $('div.checkin_numbers span.checked_in').html(newLengthChecked)
        return
    init: () ->
        scope = this
        # INVITE MODAL INIT
        $("div.guest-add-invite a.start-guest-invite").click (e) ->
            e.preventDefault()
            $('div#invite-modal').foundation('reveal', 'open')
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
        $('a.close-invite-modal').click () ->
            $('div#invite-modal').foundation('reveal', 'close')
            return
        $("div.guest-add-invite a.start-guest-add").click (e) ->
            e.preventDefault()
            $('div.add-guest-container').removeClass 'hidden'
            return
        $('form[name=add-guest]').submit (e) ->
            e.preventDefault()
            if not scope.purchaseInProgress
                scope.add_purchase()
            return
        $('form input[name=guest_name]').keyup (e) ->
            e.preventDefault()
            if $(this).val() == ''
                $('div.guest').removeClass('hide')
            else
                $('div.guest').addClass('hide')
                scope.filterGuests('name', $(this).val(), scope.selectionStatus,  scope.checkinStatus, false)
            return
        $('form input[name=guest_code]').keyup (e) ->
            e.preventDefault()
            if $(this).val() == ''
                $('div.guest').removeClass('hide')
            else
                $('div.guest').addClass('hide')
                scope.filterGuests('confirmation', $(this).val(), scope.selectionStatus,  scope.checkinStatus, false)
            return
        $('form.list_search div.ticket_filters a').click (e) ->
            e.preventDefault()
            $('form.list_search div.ticket_filters a').removeClass('active')
            $(this).addClass('active')
            $('form.list_search input[name=guest_name]').val('')
            $('form.list_search input[name=guest_code]').val('')
            $('div.guest').addClass('hide')
            scope.selectionStatus = $(this).data('id')
            scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true)
            return
        $('form.list_search div.checkin_filters a').click (e) ->
            e.preventDefault()
            $('form.list_search div.checkin_filters a').removeClass('active')
            $(this).addClass('active')
            $('form.list_search input[name=guest_name]').val('')
            $('form.list_search input[name=guest_code]').val('')
            $('div.guest').addClass('hide')
            scope.checkinStatus = $(this).data('status')
            scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true)
            return
        $('div.list_guests').on 'click', 'div.guest div.checkin a',  (e) ->
            e.preventDefault()
            guest = $(this).parents('div.guest')
            guest_id = guest.data('id')
            if not guest.hasClass('checked_in')
                checkCount = parseInt($('div.checkin_numbers span.checked_in').html()) + 1
                $('div.checkin_numbers span.checked_in').html(checkCount)
                guest.addClass('checked_in')
                $(this).html('Arrived')
                scope.checkin(guest_id)
                if scope.checkinStatus == 'not_checked_in'
                    guest.addClass('hide')
                    totalCount = parseInt($('div.checkin_numbers span.total_guests').html()) - 1
                    $('div.checkin_numbers span.total_guests').html(totalCount)
                    $('div.checkin_numbers span.checked_in').html('0')
                    Bazaarboy.adjustBottomPosition()
            else
                checkCount = parseInt($('div.checkin_numbers span.checked_in').html()) - 1
                $('div.checkin_numbers span.checked_in').html(checkCount)
                guest.removeClass('checked_in')
                $(this).html('Check In')
                scope.checkout(guest_id)
                if scope.checkinStatus == 'checked_in'
                    guest.addClass('hide')
                    totalCount = parseInt($('div.checkin_numbers span.total_guests').html()) - 1
                    $('div.checkin_numbers span.total_guests').html(totalCount)
                    $('div.checkin_numbers span.checked_in').html(totalCount)
                    Bazaarboy.adjustBottomPosition()
        return

Bazaarboy.event.manage.init()