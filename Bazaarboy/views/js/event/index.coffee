Bazaarboy.event.index = 
    init: () ->
        # RSVP
        $('div#event div.action a').click () ->
            $('div#wrapper_overlay').fadeIn(200)
            $('div#rsvp').fadeIn(200)
            return
        $('div#wrapper_overlay').click () ->
            $('div#wrapper_overlay').fadeOut(200)
            $('div#rsvp').fadeOut(200)
            return
        $('div#rsvp form.login').submit (event) ->
            event.preventDefault()
            Bazaarboy.get 'user/auth/', $(this).serializeObject()
            , (response) ->
                if response.status is 'OK'
                    window.location.hash = '#rsvp'
                    window.location.reload()
                else
                    console.log response
                return
            return
        $('div#rsvp form.register').submit (event) ->
            event.preventDefault()
            Bazaarboy.post 'user/create/', $(this).serializeObject()
            , (response) ->
                if response.status is 'OK'
                    window.location.hash = '#rsvp'
                    window.location.reload()
                else
                    console.log response
                return
            return
        $('div#rsvp form.register').submit (event) ->
            event.preventDefault()
            return
        # Redactor
        $('div.description div.editable').redactor
            buttons: [
                'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                'alignment', '|',
                'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                'image', 'video', 'link', '|',
                'horizontalrule'
            ]
            imageUpload: rootUrl
        $('div.description div.controls a.save').click () ->
            description = $('div.description div.editable').redactor('get')
            console.log description
            return
        # Check whether to open the RSVP modal
        if window.location.hash? and window.location.hash is '#rsvp'
            $('div#event div.action a').click()
        return