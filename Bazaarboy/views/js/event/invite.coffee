Bazaarboy.event.invite =
    init: () ->
        options =
            callback: (value) ->
                $(".template_container #organizer_message").html($("form.email_form textarea[name=message]").val())
                return
            wait: 750
            highlight: true
        $("form.email_form textarea[name=message]").typeWatch(options)
        return

Bazaarboy.event.invite.init()