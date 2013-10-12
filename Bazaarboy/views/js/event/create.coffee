Bazaarboy.event.create = 
    init: () ->
        $('div#event_create form.create').submit (event) ->
            event.preventDefault()
            data = $(this).serializeObject()
            startTime = moment(data.start_time).utc()
            data.start_time = startTime.format('YYYY-MM-DD HH:mm:ss')
            Bazaarboy.post 'event/create/', data, (response) ->
                if response.status is 'OK'
                    eventUrl = 'event/' + response.event.pk
                    if not loggedIn
                        eventUrl += '?token=' + response.event.access_token
                    Bazaarboy.redirect eventUrl
                else
                    console.log response
                return
            return
        return

Bazaarboy.event.create.init()