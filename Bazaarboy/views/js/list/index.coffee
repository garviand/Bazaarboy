Bazaarboy.list.index =
    init: () ->
        scope = this
        $("a.show-archived-signups").click () ->
            $("div.archived-button-container").hide()
            $("div.archived_sign_up").removeClass('hide')
        $("a.delete-signup.btn").click () ->
            list = $(this).closest("div.list")
            signupId = $(this).data("id")
            swal
                title: "Are You Sure?"
                text: "Are you sure you want to archive this signup? You can still view it by clicking the 'View Archived Signups' button."
                type: "warning"
                showCancelButton: true
                confirmButtonText: "Yes, DeArchivelete"
                closeOnConfirm: true
                , ->
                    Bazaarboy.post 'lists/signup/delete/', {id:signupId}, (response) ->
                        if response.status is 'OK'
                            list.remove()
                        else
                            swal response.message
                        return
        $("a.delete-list-btn").click () ->
            list = $(this).closest("div.list")
            listId = $(this).data("id")
            swal
                title: "Are You Sure?"
                text: "Are you sure you want to delete this list?"
                type: "warning"
                showCancelButton: true
                confirmButtonText: "Yes, Delete"
                closeOnConfirm: true
                , ->
                    Bazaarboy.post 'lists/delete/', {id:listId}, (response) ->
                        if response.status is 'OK'
                            list.remove()
                        else
                            swal response.message
                        return
        $(".new-list-btn").click () ->
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
                        Bazaarboy.redirect 'lists/' + response.list.pk
                    return
            else
                swal 'List name can\'t be empty'
            return
        return

Bazaarboy.list.index.init()