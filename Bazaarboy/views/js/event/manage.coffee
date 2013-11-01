Bazaarboy.event.manage =
    selectionStatus: 'all'
    filterGuests: (param, value, ticketType) ->
        length = $('div.guest').length
        for i in [0..length-1]
            rsvp = $('div.guest:eq(' + i + ')')
            targetValue = $(rsvp).find('div.' + param).html()
            if targetValue.toLowerCase().indexOf(value.toLowerCase()) != -1
                if rsvp.data('ticket') == ticketType or ticketType == 'all'
                    $(rsvp).removeClass('hidden')
        return
    init: () ->
        scope = this
        $('form.list_search input[name=guest_name]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_name]').val() == ''
                $('div.guest').removeClass('hidden')
            else
                $('div.guest').addClass('hidden')
                @filterGuests('name', $('form.list_search input[name=guest_name]').val(), @selectionStatus)
            return
        $('form.list_search input[name=guest_code]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_code]').val() == ''
                $('div.guest').removeClass('hidden')
            else
                $('div.guest').addClass('hidden')
                @filterGuests('confirmation', $('form.list_search input[name=guest_code]').val(), @selectionStatus)
            return
        $('form.list_search div.ticket_filters a').click (e) ->
            e.preventDefault()
            $('form.list_search div.ticket_filters a').removeClass('active')
            $(this).addClass('active')
            $('form.list_search input[name=guest_name]').val('')
            $('form.list_search input[name=guest_code]').val('')
            $('div.guest').addClass('hidden')
            scope.selectionStatus = $(this).data('id')
            scope.filterGuests('name', '', scope.selectionStatus)
        return

Bazaarboy.event.manage.init()