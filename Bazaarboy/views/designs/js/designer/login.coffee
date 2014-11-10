Bazaarboy.designs.designer.login =
    init: () ->
        $("form#login-form").submit (e) ->
            e.preventDefault()
            params = {}
            params.email = $("form#login-form input[name=email]").val()
            params.password = $("form#login-form input[name=password]").val()
            if params.email.length isnt 0 and
                params.password.length isnt 0
                    Bazaarboy.post 'designs/designer/auth/', params, (response) ->
                        if response.status is 'OK'
                            window.location.href = '/designs/designer'
                        else
                            alert 'Failed'
        return

Bazaarboy.designs.designer.login.init()