@Bazaarboy.login = 
    init: () ->
        $(window).hashchange () ->
            hash = location.hash
            if hash is '#register'
                $('div#login-container').hide()
                $('div#register-container').show()
                $('div#register-container').addClass('active')
                $('div#login div#footer a.switch').html('Login')
            else
                $('div#register-container').hide()
                $('div#login-container').show()
                $('div#login-container').addClass('active')
                $('div#login div#footer a.switch').html('Register')
            return
        $(window).hashchange()
        $('div#login div#footer a.switch').click () ->
            if $('div#login-container').hasClass('active')
                $('div#login div#footer a.switch').html('Login')
                $('div#login-container').fadeOut 300, () ->
                    $('div#register-container').fadeIn 300, () ->
                        $('div#login-container').removeClass('active')
                        $('div#register-container').addClass('active')
                        return
                    return
            else
                $('div#login div#footer a.switch').html('Register')
                $('div#register-container').fadeOut 300, () ->
                    $('div#login-container').fadeIn 300, () ->
                        $('div#register-container').removeClass('active')
                        $('div#login-container').addClass('active')
                        return
                    return
            return
        $('form#login-form input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form#login-form').submit()
            return
        $('form#login-form').submit (event) ->
            event.preventDefault()
            params = $('form#login-form').serializeObject()
            params = Bazaarboy.trim params
            if params.email.length isnt 0 and
                params.password.length isnt 0
                    Bazaarboy.get 'user/auth/', params, (response) ->
                        if response.status is 'OK'
                            Bazaarboy.redirect 'index'
                        else
                            alert response.message
                        return
            return
        $('form#register-form input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form#register-form').submit()
            return
        $('form#register-form').submit (event) ->
            event.preventDefault()
            params = $('form#register-form').serializeObject()
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

Bazaarboy.login.init()