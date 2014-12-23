Bazaarboy.event.invite =
    saving: false
    init: () ->
        scope = this
        $('a.save-invite').click () ->
            if not scope.saving
                scope.saving = true
                eventId = $('div.email input[name=event]').val()
                message = $('div.email textarea[name=message]').val()
                if message.trim() is ''
                    swal("Wait!", "Email Message Cannot Be Empty", "warning")
                    scope.saving = false
                    return
                details = $('div.email textarea[name=details]').val()
                lists = '1'
                console.log eventId, message, details, lists
                Bazaarboy.post 'event/invite/new/', {id:eventId, message:message, details:details, lists:lists}, (response) ->
                    if response.status is 'OK'
                        inviteId = response.invite.pk
                        Bazaarboy.redirect 'event/invite/' + inviteId + '/preview'
                    scope.saving = false
                    return
            return
        return
        
Bazaarboy.event.invite.init()