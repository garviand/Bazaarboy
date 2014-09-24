@Bazaarboy.user.login = 
    init: () ->
        $('form[name=login]').submit (event) ->
            event.preventDefault()
            params = $('form[name=login]').serialize()
            Bazaarboy.post 'user/auth/', params, (response) ->
                if response.status is 'OK'
                    Bazaarboy.redirect 'index'
                else
                    alert response.message
            return
        return

fbSDKReady = () ->
    FB.getLoginStatus (response) ->
        if response.status is 'connected'
            fbAccessToken = response.authResponse.accessToken
            console.log fbAccessToken