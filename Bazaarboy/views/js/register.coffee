@Bazaarboy.user.register =
    init: =>
        $(document).ready =>
            $('form[name=register]').submit (event) =>
                event.preventDefault()
                return
            return
        return

window.fbSDKReady = () ->
    FB.getLoginStatus (response) ->
        if response.status is 'connected'
            fbAccessToken = response.authResponse.accessToken
            console.log fbAccessToken
        else
            email = $('input[name=email]').val()
            $('a#fb_login').click () ->
                FB.login (response) ->
                    if response.authResponse
                        fbAccessToken = response.authResponse.accessToken
                        console.log fbAccessToken