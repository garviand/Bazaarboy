@Bazaarboy.login = 
    timer: undefined
    rotateLogo: (degree) ->  
        $('div.logo-small').css({ WebkitTransform: 'rotate(' + degree + 'deg)'}) 
        $('div.logo-small').css({ '-moz-transform': 'rotate(' + degree + 'deg)'})                      
        @timer = setTimeout (() =>
            @rotateLogo(++degree)
            return
        ),5
        return
    init: () ->
        scope = this
        $('form#login-form input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form#login-form').submit()
            return
        $('form#login-form').submit (event) ->
            event.preventDefault()
            scope.rotateLogo(0)
            params = $('form#login-form').serializeObject()
            params = Bazaarboy.trim params
            if params.email.length isnt 0 and
                params.password.length isnt 0
                    Bazaarboy.post 'user/auth/', params, (response) ->
                        if response.status is 'OK'
                            Bazaarboy.redirect 'index'
                        else
                            alert response.message
                            window.clearTimeout(scope.timer)
                            $('div.logo-small').css({ WebkitTransform: 'none'}) 
                            $('div.logo-small').css({ '-moz-transform': 'none'})
                        return
            return
        $('form#register-form input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form#register-form').submit()
            return
        $('form#register-form').submit (event) ->
            console.log 'Submit Register Form'
            event.preventDefault()
            scope.rotateLogo(0)
            params = $('form#register-form').serializeObject()
            params = Bazaarboy.trim params
            if params.email.length isnt 0 and
                params.password.length isnt 0 and
                params.password is params.confirm and
                params.first_name.length isnt 0 and
                params.last_name.length isnt 0
                    Bazaarboy.post 'user/create/', params, (response) ->
                        console.log response
                        if response.status is 'OK'
                            Bazaarboy.redirect 'index'
                        else
                            alert response.message
                            window.clearTimeout(scope.timer)
                            $('div.logo-small').css({ WebkitTransform: 'none'}) 
                            $('div.logo-small').css({ '-moz-transform': 'none'})
                        return
            else if params.password isnt params.confirm
                alert "Passwords do not match"
                window.clearTimeout(scope.timer)
                $('div.logo-small').css({ WebkitTransform: 'none'}) 
                $('div.logo-small').css({ '-moz-transform': 'none'})
            else
                alert "All fields must be filled out"
                window.clearTimeout(scope.timer)
                $('div.logo-small').css({ WebkitTransform: 'none'}) 
                $('div.logo-small').css({ '-moz-transform': 'none'})
            return
        return

Bazaarboy.login.init()