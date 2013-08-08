@Bazaarboy.user.register =
    init: () ->
        $('form[name=register]').submit (event) ->
            event.preventDefault()
            return
        return
    fbAuth: (fbAccessToken, email='', city='') ->
        console.log city
        Bazaarboy.post 'user/fbAuth/', 
            fb_token: fbAccessToken
            email: email
            city: city
        , (response) ->
            if response.status is 'OK'
                Bazaarboy.redirect 'index'
            else
                alert response.message
            return
        return        

window.fbSDKReady = () ->
    FB.getLoginStatus (response) ->
        if response.status is 'connected'
            fbAccessToken = response.authResponse.accessToken
            $('a#fb_login').click () ->
                email = $('input[name=email]').val()
                city = $('input[name=city]').val()
                Bazaarboy.user.register.fbAuth fbAccessToken, email, city
                return
        else
            $('a#fb_login').click () ->
                email = $('input[name=email]').val()
                city = $('input[name=city]').val()
                FB.login (response) ->
                    if response.authResponse
                        fbAccessToken = response.authResponse.accessToken
                        Bazaarboy.user.register.fbAuth fbAccessToken, email, city
                    return
                return
        return      