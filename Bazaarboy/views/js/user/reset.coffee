@Bazaarboy.user.reset = 
    init: () ->
        $('form#reset-form').submit (event) ->
            event.preventDefault()
            $('input.submit-reset').val 'Sending...'
            params = $('form#reset-form').serializeObject()
            Bazaarboy.post 'user/reset/create/', params, (response) ->
                if response.status is 'OK'
                    $('form#reset-form div.reset-form-content').fadeOut 300, () ->
                        $('form#reset-form div.reset-form-confirmation').fadeIn 300
                        return
                else
                    alert response.message
                    $('input.submit-reset').val 'Send Reset Request'
            return
        $('form#password-form').submit (event) ->
            event.preventDefault()
            $('input.submit-password').val 'Changing Password...'
            params = $('form#password-form').serializeObject()
            Bazaarboy.post 'user/password/change/', params, (response) ->
                if response.status is 'OK'
                    $('form#password-form div.password-form-content').fadeOut 300, () ->
                        $('form#password-form div.password-form-confirmation').fadeIn 300
                        return
                else
                    alert response.message
                    $('input.submit-password').val 'Reset Password'
            return
        return

@Bazaarboy.user.reset.init()