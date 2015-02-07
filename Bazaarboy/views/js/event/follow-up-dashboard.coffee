Bazaarboy.event.follow_up_dashboard =
    init: () ->
        scope = this
        $('div.comm a.delete-follow-up').click () ->
            follow_up = $(this).closest('div.comm')
            follow_up_id = $(this).data('id')
            swal
                title: "Are You Sure?"
                text: "Are you sure you want to delete this follow up draft?"
                type: "warning"
                showCancelButton: true
                confirmButtonText: "Yes"
                closeOnConfirm: true
                , ->
                    Bazaarboy.post 'event/followup/delete/', {id:follow_up_id}, (response) ->
                        if response.status is 'OK'
                            follow_up.remove()
                        else
                            console.log response
                        return
                    return
        return
        
Bazaarboy.event.follow_up_dashboard.init()