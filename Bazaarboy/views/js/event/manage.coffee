Bazaarboy.event.manage =
    filterGuests: (param, value) ->
        length = $('div.guest').length
        for i in [0..length-1]
            rsvp = $('div.guest:eq(' + i + ')')
            targetValue = $(rsvp).find('div.' + param).html()
            if targetValue.toLowerCase().indexOf(value.toLowerCase()) != -1
                $(rsvp).removeClass('hidden')
        return
    init: () ->
        $('form.list_search input[name=guest_name]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_name]').val() == ''
                $('div.guest').removeClass('hidden')
            else
                $('div.guest').addClass('hidden')
                @filterGuests('name', $('form.list_search input[name=guest_name]').val())
        $('form.list_search input[name=guest_code]').keyup (e) =>
            e.preventDefault()
            if $('form.list_search input[name=guest_code]').val() == ''
                $('div.guest').removeClass('hidden')
            else
                $('div.guest').addClass('hidden')
                @filterGuests('confirmation', $('form.list_search input[name=guest_code]').val())
        return

Bazaarboy.event.manage.init()