Bazaarboy.event.manage =
    selectionStatus: 'all'
    checkinStatus: 'all'
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
                if rsvp.data('ticket') == ticketType or ticketType == 'all'
                    $(rsvp).removeClass('hidden')
            if(checkStatus == 'checked_in')
                console.log('Arrived Only')
                if not $(rsvp).hasClass('checked_in')
                    $(rsvp).addClass('hidden')
            if(checkStatus == 'not_checked_in')
                console.log('Not Checked In Only')
                if $(rsvp).hasClass('checked_in')
                    $(rsvp).addClass('hidden')
        if updateListLength
            newLength = $('div.guest').not('.hidden').length
            newLengthChecked = $('div.guest.checked_in').not('.hidden').length
            $('div.checkin_count div.checkin_numbers span.total_guests').html(newLength)
            $('div.checkin_count div.checkin_numbers span.checked_in').html(newLengthChecked)
        Bazaarboy.adjustBottomPosition()
        return
    init: () ->
        scope = this
        $('form.list_search input[name=guest_name]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_name]').val() == ''
                $('div.guest').removeClass('hidden')
            else
                $('div.guest').addClass('hidden')
                @filterGuests('name', $('form.list_search input[name=guest_name]').val(), @selectionStatus, @checkinStatus, false)
            return
        $('form.list_search input[name=guest_code]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_code]').val() == ''
                $('div.guest').removeClass('hidden')
            else
                $('div.guest').addClass('hidden')
                @filterGuests('confirmation', $('form.list_search input[name=guest_code]').val(), @selectionStatus,  @checkinStatus, false)
            return
        $('form.list_search div.ticket_filters a').click (e) ->
            e.preventDefault()
            $('form.list_search div.ticket_filters a').removeClass('active')
            $(this).addClass('active')
            $('form.list_search input[name=guest_name]').val('')
            $('form.list_search input[name=guest_code]').val('')
            $('div.guest').addClass('hidden')
            scope.selectionStatus = $(this).data('id')
            scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true)
            return
        $('form.list_search div.checkin_filters a').click (e) ->
            e.preventDefault()
            $('form.list_search div.checkin_filters a').removeClass('active')
            $(this).addClass('active')
            $('form.list_search input[name=guest_name]').val('')
            $('form.list_search input[name=guest_code]').val('')
            $('div.guest').addClass('hidden')
            scope.checkinStatus = $(this).data('status')
            scope.filterGuests('name', '', scope.selectionStatus, scope.checkinStatus, true)
            return
        $('div.list_guests div.guest div.checkin a').click (e) ->
            e.preventDefault()
            guest = $(this).parents('div.guest')
            guest_id = guest.data('id')
            if not guest.hasClass('checked_in')
                checkCount = parseInt($('div.checkin_count div.checkin_numbers span.checked_in').html()) + 1
                $('div.checkin_count div.checkin_numbers span.checked_in').html(checkCount)
                guest.addClass('checked_in')
                $(this).html('Arrived')
                scope.checkin(guest_id)
                if scope.checkinStatus == 'not_checked_in'
                    guest.addClass('hidden')
                    totalCount = parseInt($('div.checkin_count div.checkin_numbers span.total_guests').html()) - 1
                    $('div.checkin_count div.checkin_numbers span.total_guests').html(totalCount)
                    $('div.checkin_count div.checkin_numbers span.checked_in').html('0')
                    Bazaarboy.adjustBottomPosition()
            else
                checkCount = parseInt($('div.checkin_count div.checkin_numbers span.checked_in').html()) - 1
                $('div.checkin_count div.checkin_numbers span.checked_in').html(checkCount)
                guest.removeClass('checked_in')
                $(this).html('Check In')
                scope.checkout(guest_id)
                if scope.checkinStatus == 'checked_in'
                    guest.addClass('hidden')
                    totalCount = parseInt($('div.checkin_count div.checkin_numbers span.total_guests').html()) - 1
                    $('div.checkin_count div.checkin_numbers span.total_guests').html(totalCount)
                    $('div.checkin_count div.checkin_numbers span.checked_in').html(totalCount)
                    Bazaarboy.adjustBottomPosition()
        return

Bazaarboy.event.manage.init()