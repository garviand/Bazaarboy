Bazaarboy.index.index = 
    createEvent: (profileId) ->
        Bazaarboy.post 'event/create/', {profile: profileId}, (response) =>
            if response.status is 'OK'
                Bazaarboy.redirect 'event/' + response.event.pk + '/basics/'
            else
                alert response.message
            return
        return
    init: () ->
        scope = this
        # Create event
        $('div.action-btn.create-event').click () ->
            profileId = $(this).attr('data-profile-id')
            scope.createEvent profileId
            return
        return

Bazaarboy.index.index.init()