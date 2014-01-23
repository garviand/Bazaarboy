Bazaarboy.event.invite =
    init: () ->
        typewatch_options =
            callback: (value) ->
                $(".template_container #organizer_message").html($("form.email_form textarea[name=message]").val())
                return
            wait: 750
            highlight: true
        $("form.email_form textarea[name=message]").typeWatch(typewatch_options)
        $('input[name=include_cover]').change () ->
            if $(this).is(':checked')
                $(".template_container #cover_image").show()
            else
                $(".template_container #cover_image").hide()
            return
        return

Bazaarboy.event.invite.init()