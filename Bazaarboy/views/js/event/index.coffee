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
        return