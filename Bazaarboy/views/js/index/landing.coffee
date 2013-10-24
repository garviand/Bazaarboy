@Bazaarboy.landing = 
    init: () ->
    	$('form[name=login] input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form[name=login]').submit()
            return
        $('#landing .inner .login_content .bottom a.login_btn').click () ->
            $('form[name=login]').submit()
            return
        $('form[name=login]').submit (event) ->
            console.log "log in now"
            event.preventDefault()
            params = $('form[name=login]').serialize()
            Bazaarboy.get 'user/auth/', params, (response) ->
                if response.status is 'OK'
                    Bazaarboy.redirect 'index'
                else
                    alert response.message
            return
        $('#landing .inner .starting_content .bottom .login_link_container .start_sign_in').click () ->
            $('#landing .inner .starting_content').addClass 'hidden'
            $('#landing .inner .login_content').removeClass 'hidden'
            return
        $('#landing .inner .login_content .bottom a.back').click () ->
            $('#landing .inner .login_content').addClass 'hidden'
            $('#landing .inner .starting_content').removeClass 'hidden'
            return
        return

Bazaarboy.landing.init()