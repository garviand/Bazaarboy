Bazaarboy.event.index = 
    description: undefined
    initTransaction: () ->
        # Account control
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
        # Check whether to open the RSVP modal
        if window.location.hash? and window.location.hash is '#rsvp' and editable
            $('div#event div.action').click()
        return
    save: (params, cb) ->
        params.id = eventId
        if token?
            params.token = token
        Bazaarboy.post 'event/edit/', params, (response) ->
            if response.status is 'OK'
                return cb null, response.event
            else
                err = 
                    error: response.error
                    message: response.message
                return cb err, null
            return
        return
    startEditingDescription: () ->
        $('div.description div.controls a.edit').html('Cancel')
        $('div.description div.controls a.save').show()
        $('div.description div.editor').addClass('editing')
        $('div.description div.editor div.inner').redactor
            buttons: [
                'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                'alignment', '|',
                'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                'image', 'video', 'link', '|',
                'html'
            ]
            boldTag: 'b'
            italicTag: 'i'
        return
    stopEditingDescription: (description) ->
        $('div.description div.controls a.edit').html('Edit')
        $('div.description div.controls a.save').hide()
        $('div.description div.editor').removeClass('editing')
        $('div.description div.editor div.inner').redactor('destroy')
        $('div.description div.editor div.inner').html(description)
        return
    saveDescription: () ->
        description = $('div.description div.editor div.inner').redactor('get')
        @save {description: description}, (err, event) =>
            unless err
                @description = event.description
                @stopEditingDescription @description
            else
                alert err.message
            return
        return
    initEditing: () ->
        # Edit description
        @description = $('div#event div.description div.inner').html()
        $('div#event div.description div.controls a.save').hide().click () =>
            @saveDescription()
        $('div#event div.description div.controls a.edit').click () =>
            if $('div.description div.editor').hasClass('editing')
                @stopEditingDescription @description
            else
                @startEditingDescription()
            return
        return
    init: () ->
        # Extend collapse animations
        collapseStates = [
            ['div#event', [['margin-left', '63px', '96px']]]
            ['div#event.big_cover div.cover', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#event > div.title', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#event > div.title div.text', [['left', '63px', '96px']]]
        ]
        $.merge(Bazaarboy.collapseStates, collapseStates)
        # Overlay
        $('div#event div.action').click () ->
            $('div#wrapper_overlay').fadeIn(200)
            $('div.event_overlay_canvas').fadeIn(200)
            return
        $('div#wrapper_overlay').click () ->
            $('div#wrapper_overlay').fadeOut(200)
            $('div.event_overlay_canvas').fadeOut(200)
            return
        # Further initialization
        if editable then @initEditing() else @initTransaction()
        return

Bazaarboy.event.index.init()