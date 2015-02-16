Bazaarboy.event.invite_dashboard =
    sending: false
    init: () ->
        scope = this
        $('a.create-invite-btn').click () ->
            if numLists is 0
                swal
                    title: "Hold On!"
                    text: "Before sending an invite, create a list of contacts (ie friends, guests) to notify."
                    type: "warning"
                    showCancelButton: true
                    confirmButtonText: "Create List"
                    closeOnConfirm: true
                    , ->
                        $("div#new-list-modal").foundation('reveal', 'open')
                        return
        $("a.close-list-modal").click () ->
            $("div#new-list-modal").foundation('reveal', 'close')
            return
        $("div#new-list-modal div.new-list-inputs a.create-list").click () ->
            $(this).html 'Creating...'
            list_name = $("div#new-list-modal div.new-list-inputs input[name=list_name]").val()
            if list_name.trim() isnt ''
                Bazaarboy.post 'lists/create/', {profile:profileId, name:list_name, is_hidden:1}, (response) ->
                    if response.status is 'OK'
                        Bazaarboy.redirect 'lists/' + response.list.pk + '/?eid=' + String(eventId)
                    return
            else
                swal 'List name can\'t be empty'
            return
        $('div.comm a.copy-invite').click () ->
            inviteId = $(this).data('id')
            Bazaarboy.post 'event/invite/' + inviteId + '/copy/', {}, (response) ->
                if response.status is 'OK'
                    Bazaarboy.redirect 'event/invite/'+response.invite.pk+'/edit/'
                else
                    swal response.message
                return
            return
        $('div.comm a.delete-invite').click () ->
            invitation = $(this).closest('div.comm')
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