Bazaarboy.event.format_full_screen =
    init: () ->
        $("form.hero-ticket-form button[type=submit]").click (e) ->
            e.preventDefault()
            ticketId = $("form.hero-ticket-form .tix-type").data('id')
            if not $("div#tickets div.ticket[data-id=" + ticketId + "]").hasClass('active')
                $("div#tickets div.ticket[data-id=" + ticketId + "] div.ticket-top").click()
            if not Bazaarboy.event.index.overlayAnimationInProgress
                $("html, body").animate({ scrollTop: 0 }, "fast")
                if $('div#wrapper-overlay').hasClass('hide')
                    Bazaarboy.event.index.overlayAnimationInProgress = true
                    $('div#wrapper-overlay').css('opacity', 0).removeClass('hide')
                    $('div#tickets').css('opacity', 0).removeClass('hide')
                    $('div#wrapper-overlay').animate {opacity: 1}, 300
                    $('div#tickets').animate {opacity: 1}, 300, () =>
                        Bazaarboy.event.index.overlayAnimationInProgress = false
                        return
        return

Bazaarboy.event.format_full_screen.init()