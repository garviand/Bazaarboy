Bazaarboy.event.invite_dashboard =
    sending: false
    init: () ->
        scope = this
        $('div.invitation a.copy-invite').click () ->
            inviteId = $(this).data('id')
            Bazaarboy.post 'event/invite/' + inviteId + '/copy/', {}, (response) ->
                if response.status is 'OK'
                    Bazaarboy.redirect 'event/invite/'+response.invite.pk+'/edit/'
                else
                    swal response.message
                return
            return
        $('div.invitation a.delete-invite').click () ->
            invitation = $(this).closest('div.invitation')
            inviteId = $(this).data('id')
            swal
                title: "Are You Sure?"
                text: "Are you sure you want to delete this invitation draft?"
                type: "warning"
                showCancelButton: true
                confirmButtonText: "Yes"
                closeOnConfirm: true
                , ->
                    Bazaarboy.post 'event/invite/delete/', {id:inviteId}, (response) ->
                        if response.status is 'OK'
                            invitation.remove()
                        else
                            console.log response
                        return
                    return
        return
        
Bazaarboy.event.invite_dashboard.init()