Bazaarboy.event.index = 
    startDescriptionEdit: (cb) ->
        $('div.description div.editor').addClass('editable')
        $('div.description div.editor div.inner').redactor
            buttons: [
                'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                'alignment', '|',
                'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                'image', 'video', 'link', '|',
                'horizontalrule'
            ]
            imageUpload: rootUrl
        return
    stopDescriptionEdit: (cb) ->
        $('div.description div.editor').removeClass('editable')
        $('div.description div.editor div.inner').redactor('destroy')
        return
    init: () ->
        # Extend collapse animations
        collapseStates = [
            ['div#event', [['margin-left', '63px', '96px']]]
            ['div#event.big_cover div.cover', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#event div.title', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
        ]
        $.merge(Bazaarboy.collapseStates, collapseStates)
        # RSVP
        $('div#event div.action').click () ->
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
        $('div#event div.description div.controls a.save').click () =>
            if $('div.description div.editor').hasClass('editable')
                @stopDescriptionEdit()
            else
                @startDescriptionEdit()
            return
        # Check whether to open the RSVP modal
        if window.location.hash? and window.location.hash is '#rsvp'
            $('div#event div.action').click()
        return

Bazaarboy.event.index.init()