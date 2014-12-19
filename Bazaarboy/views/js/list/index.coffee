Bazaarboy.list.index =
    init: () ->
        scope = this
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
                alert 'List name can\'t be empty'
            return
        return

Bazaarboy.list.index.init()