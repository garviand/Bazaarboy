Bazaarboy.event.invite_dashboard =
    sending: false
    init: () ->
        scope = this
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