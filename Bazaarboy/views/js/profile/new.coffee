Bazaarboy.profile.new = 
    init: () ->
        $('form.profile-new').submit (event) ->
            event.preventDefault()
            params = $(this).serializeObject()
            optionals = [
               'email', 'phone', 'link_website', 'link_facebook', 'EIN'
            ]
            params = Bazaarboy.stripEmpty params, optionals
            Bazaarboy.post 'profile/create/', params, (response) ->
                if response.status is 'OK'
                  Bazaarboy.redirect 'index'
                else
                  alert response.message
                return
            return
        return

Bazaarboy.profile.new.init()