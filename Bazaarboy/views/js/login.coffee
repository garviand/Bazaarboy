@Bazaarboy.user.login = 
    init: =>
        $(document).ready =>
            $('form[name=login]').submit (event) =>
                event.preventDefault()
                params = $('form[name=login]').serialize()
                Bazaarboy.get 'user/auth/', params, (response) =>
                    if response.status is 'OK'
                        Bazaarboy.redirect 'index'
                    else
                        alert response.message
                return
            return
        return