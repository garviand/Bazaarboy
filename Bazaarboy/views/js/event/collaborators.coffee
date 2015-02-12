Bazaarboy.event.collaborators =
    sending: false
    search_organizers: () ->
        $('form.add-organizer-form div.organizer').remove()
        organizerModel = $('div.organizer-model')
        value = $('form.add-organizer-form input#organizer-name').val()
        Bazaarboy.get 'profile/search/', {keyword: value}, (response) =>
            if response.status is 'OK'
                profiles = response.profiles
                if profiles.length > 0
                    $('.profile_login .profile_choices').empty()
                    for i in [0..profiles.length-1]
                        newProfile = organizerModel
                        newProfile.find('div.organizer-name').html(profiles[i].name)
                        if profiles[i].image_url?
                            newProfile.find('div.organizer-image').html('<img src='+profiles[i].image_url+' />')
                        else
                            newProfile.find('div.organizer-image').html('&nbsp;')
                        newProfile.find('a.add-organizer-submit').attr('data-profile', profiles[i].pk)
                        $('form.add-organizer-form').append(newProfile.html())
            return
        return
    init: () ->
        scope = this
        # TOGGLE ORGANIZER VISIBLE
        $('a.toggle-visiblity-btn').click () ->
            organizerId = $(this).data('organizer')
            console.log organizerId
            Bazaarboy.post 'event/collaborator/' + organizerId + '/toggle/', {}, (response) ->
                if response.status is 'OK'
                    if response.organizer.is_public
                        $('a.toggle-visiblity-btn').html('Hide on Event')
                    else
                        $('a.toggle-visiblity-btn').html('Show on Event')
                else
                    swal response.message
                return
            return
        # ADD ORGANIZER
        $('a.add-organizer-btn').click () ->
            $('div#add-organizer-modal').foundation('reveal', 'open')
            return
        $('a.add-organizer-close').click () ->
            $('div#add-organizer-modal').foundation('reveal', 'close')
            return
        $('a.add-organizer-another').click () ->
            $('div.row.add-organizer-success').fadeOut 300, () ->
                $('form.add-organizer-form').fadeIn 300
                return
            return
        add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers)
        $('form.add-organizer-form input#organizer-name').bind('keypress', add_organizer_debounce)
        $('form.add-organizer-form').on 'click', 'a.add-organizer-submit', () ->
            profileId = $(this).data('profile')
            Bazaarboy.post 'event/organizer/request/', {id: eventId, profile: profileId}, (response) =>
                if response.status is 'OK'
                    $('form.add-organizer-form').fadeOut 300, () ->
                        $('form.add-organizer-form input#organizer-name').val('')
                        $('form.add-organizer-form div.organizer').remove()
                        $('div.row.add-organizer-success').fadeIn 300
                        newReq = $('div.request_template').clone()
                        newReq.find('div.request_name').html(response.collaboration.profile.name)
                        newReq.removeClass('request_template')
                        newReq.removeClass('hide')
                        $('div.pending').append(newReq)
                        $('div.pending').removeClass('hide')
                        return
                else
                    swal response.message
                return
            return
        $('form.add-organizer-form a.send-request-btn').click () ->
            email = $('form.add-organizer-form input[name=organizer_email]').val()
            if email.trim() != ''
                Bazaarboy.post 'event/organizer/request/', {id: eventId, email: email}, (response) =>
                    if response.status is 'OK'
                        $('form.add-organizer-form').fadeOut 300, () ->
                            $('form.add-organizer-form input#organizer-name').val('')
                            $('form.add-organizer-form div.organizer').remove()
                            $('div.row.add-organizer-success').fadeIn 300
                            newReq = $('div.request_template').clone()
                            newReq.find('div.request_name').html(response.collaboration.email)
                            newReq.removeClass('request_template')
                            newReq.removeClass('hide')
                            $('div.pending').append(newReq)
                            $('div.pending').removeClass('hide')
                            return
                    else
                        swal response.message
                    return
            return
        return
        
Bazaarboy.event.collaborators.init()