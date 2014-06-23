Bazaarboy.event.modify =
    switchLaunchState: (eventId) ->
        if $('div#wrapper-sidebar div.launch-event').hasClass('launched')
            if confirm('Are you sure you want to take the event offline?')
                Bazaarboy.post 'event/delaunch/', {id: eventId}, (response) =>
                    if response.status is 'OK'
                        $('div#wrapper-sidebar div.launch-event')
                            .removeClass('launched')
                            .find('.launch-text').html('Launch Event')
                    else
                        alert response.message
                    return
        else
            Bazaarboy.post 'event/launch/', {id: eventId}, (response) =>
                if response.status is 'OK'
                    window.location = eventUrl + '#launch'
                else
                    alert response.message
                return
        return
    init: () ->
        $('div#wrapper-sidebar div.launch-event').click () =>
            if not $('div#wrapper-sidebar div.launch-event').hasClass('launched')
                $('div#wrapper-sidebar div.launch-event span.launch-text').html("Launching...")
            @switchLaunchState $('div#wrapper-sidebar div.launch-event').data('event-id')
            return
        return
        
Bazaarboy.event.modify.init()