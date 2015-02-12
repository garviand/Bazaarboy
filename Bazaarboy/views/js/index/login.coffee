@Bazaarboy.login = 
    aviary: undefined
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
                            if redirect
                                if redirect is 'designs'
                                    if code
                                        window.location.href = "/designs/finalize?code=" + code
                                    else
                                        window.location.href = "/designs?auth=true"
                            else
                                Bazaarboy.redirect 'index'
                        else
                            alert response.message
                            window.clearTimeout(scope.timer)
                            $('div.logo-small').css({ WebkitTransform: 'none'}) 
                            $('div.logo-small').css({ '-moz-transform': 'none'})
                        return
            return
        # LOGO UPLOAD
        scope.aviary = new Aviary.Feather
            apiKey: 'ce3b87fb1edaa22c'
            apiVersion: 3
            enableCORS: true
            onSave: (imageId, imageUrl) =>
                $("img#organization-logo").attr 'src', imageUrl
                scope.aviary.close();
                $('a.upload-logo-btn').html 'Uploading...'
                Bazaarboy.post 'file/aviary/profile/',
                    url: imageUrl
                , (response) ->
                    $("img#organization-logo").attr 'src', response.image
                    $("input[name=logo_id]").val(response.image_id)
                    $('a.upload-logo-btn').html 'Change'
                    return
                return
        $('a.upload-logo-btn').click () ->
            $('input[name=image_file]').click()
            return
        $('form.upload-logo input[name=image_file]').fileupload
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    $('img#organization-logo').attr 'src', mediaUrl + response.image.source
                    scope.aviary.launch
                        image: 'organization-logo'
                        url: mediaUrl + response.image.source
                        cropPresets: ['400x400']
                        cropPresetsStrict: true
                        forceCropPreset: ['Logo Size','1:1']
                else
                    swal response.message
                return
        $('form#register-form input').keypress (event) ->
            if event.which == 13
                event.preventDefault()
                $('form#register-form').submit()
            return
        $('form#register-form').submit (event) ->
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
                            if redirect
                                if redirect is 'designs'
                                    if code
                                        window.location.href = "/designs/finalize?code=" + code
                                    else
                                        window.location.href = "/designs?auth=true"
                            else
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