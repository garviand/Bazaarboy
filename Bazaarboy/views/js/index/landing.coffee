@Bazaarboy.landing = 
    init: () ->
    	$('form.login input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form.login').submit()
            return
        $('form.login').submit (event) ->
            event.preventDefault()
            params = $('form.login').serializeObject()
            params = Bazaarboy.trim params
            if params.email.length isnt 0 and
                params.password.length isnt 0
                    Bazaarboy.post 'user/auth/', params, (response) ->
                        if response.status is 'OK'
                            Bazaarboy.redirect 'index'
                        else
                            alert response.message
                        return
            return
        $('form.register input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form.register').submit()
            return
        $('form.register').submit (event) ->
            event.preventDefault()
            params = $('form.register').serializeObject()
            params = Bazaarboy.trim params
            if params.email.length isnt 0 and
                params.password.length isnt 0 and
                params.password is params.confirm and
                params.first_name.length isnt 0 and
                params.last_name.length isnt 0
                    Bazaarboy.post 'user/create/', params, (response) ->
                        if response.status is 'OK'
                            Bazaarboy.redirect 'index'
                        else
                            alert response.message
                        return
            return
        return

Bazaarboy.landing.init()