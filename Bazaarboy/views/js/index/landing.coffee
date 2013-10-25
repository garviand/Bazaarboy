@Bazaarboy.landing = 
    init: () ->
    	$('form[name=login] input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form[name=login]').submit()
            return
        $('#landing div.login_content a.login_btn').click () ->
            $('form[name=login]').submit()
            return
        $('form[name=login]').submit (event) ->
            event.preventDefault()
            params = $('form[name=login]').serializeObject()
            if params.email.trim().length isnt 0 and params.password.trim().length isnt 0
                Bazaarboy.get 'user/auth/', params, (response) ->
                    if response.status is 'OK'
                        Bazaarboy.redirect 'index'
                    else
                        alert response.message
                    return
            return
        $('#landing div.starting_content a.start_sign_in').click () ->
            $('#landing div.starting_content').addClass 'hidden'
            $('#landing div.login_content').removeClass 'hidden'
            return
        $('#landing div.login_content a.back').click () ->
            $('#landing div.login_content').addClass 'hidden'
            $('#landing div.starting_content').removeClass 'hidden'
            return
        return

Bazaarboy.landing.init()