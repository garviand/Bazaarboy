Bazaarboy.event.manage =
    selectionStatus: 'all'
    checkinStatus: 'all'
    add_purchase: (ticket, email=null, fullName=null, phone=null) ->
        @purchaseInProgress = true
        $('div#rsvp div.action a.confirm').css('display', 'none')
        $('div#rsvp div.action div.loading').removeClass('hide')
        params = 
            ticket: ticket
        if email? and fullName?
            params.email = email
            params.full_name = fullName
        if phone?
            params.phone = phone
        Bazaarboy.post 'event/purchase/add/', params, (response) =>
            if response.status is 'OK'
                $('form.add_purchase_form div.ticket_types a').removeClass('active')
                $('div.list_content div.inner div.add_purchase').fadeOut 400, (e) ->
                    $('form.add_purchase_form input[name=guest_email]').val('')
                    $('form.add_purchase_form input[name=guest_name]').val('')
                    $('form.add_purchase_form input[name=guest_phone]').val('')
                    guest_div = $('<div class="guest" data-ticket="' + response.purchase.ticket + '" data-id="' + response.purchase.pk + '"></div>')
                    guest_div.append('<div class="name">' + fullName + '</div>')
                    guest_div.append('<div class="ticket_name">' + response.purchase.ticket.name + '</div>')
                    guest_div.append('<div class="confirmation">' + response.purchase.code + '</div>')
                    guest_div.append('<div class="checkin"><a href="javascript:;">Check In</a></div>')
                    guest_div.append('<div class="clear">&nbsp;</div>')
                    $('div.list_content div.list_guests div.list_headers').after(guest_div)
                    totalCount = parseInt($('div.checkin_numbers span.total_guests').html()) + 1
                    $('div.checkin_numbers span.total_guests').html(totalCount)
                    $('div.list_content div.inner div.add_purchase').fadeIn()
                    return
            else
                alert response.message
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
        $("div.list_filters a.add_purchase_start").click (e) ->
            e.preventDefault()
            $(this).fadeOut 300, (e) ->
                $("div.list_filters div.add_purchase").removeClass('hide')
                return
            return
        $('form.add_purchase_form a.add_purchase_submit').click (e) ->
            if $('form.add_purchase_form div.ticket_types a.active').length > 0
                ticket = $('form.add_purchase_form div.ticket_types a.active').attr('data-id')
                email = $('form.add_purchase_form input[name=guest_email]').val()
                fullName = $('form.add_purchase_form input[name=guest_name]').val()
                phone = $('form.add_purchase_form input[name=guest_phone]').val()
                if email.trim() is ''
                    alert 'You must enter a valid email address.'
                    return
                if fullName.trim() is ''
                    alert 'You must enter your full name,'
                    return
                if phone.trim() is ''
                    phone = null
                scope.add_purchase ticket, email, fullName, phone
            else
                alert 'No ticket selected.'
            return
        $('form.add_purchase_form div.ticket_types a').click (e) ->
            e.preventDefault()
            $('form.add_purchase_form div.ticket_types a').removeClass('active')
            $(this).addClass('active')
            return
        $('form.list_search input[name=guest_name]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_name]').val() == ''
                $('div.guest').removeClass('hide')
            else
                $('div.guest').addClass('hide')
                @filterGuests('name', $('form.list_search input[name=guest_name]').val(), @selectionStatus,  @checkinStatus, false)
            return
        $('form.list_search input[name=guest_code]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_code]').val() == ''
                $('div.guest').removeClass('hide')
            else
                $('div.guest').addClass('hide')
                @filterGuests('confirmation', $('form.list_search input[name=guest_code]').val(), @selectionStatus,  @checkinStatus, false)
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