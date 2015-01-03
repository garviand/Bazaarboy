Bazaarboy.event.invite_preview =
    sending: false
    init: () ->
        scope = this
        $('div.email-actions a.send-email').click () ->
            if not scope.sending
                button = $(this)
                button.html 'Sending...'
                scope.sending = true
                inviteId = $(this).data('id')
                Bazaarboy.post 'event/invite/send/', {id:inviteId}, (response) ->
                    console.log response
                    scope.sending = false
                    button.html 'Send Email'
                    return
                return
        return
        
Bazaarboy.event.invite_preview.init()