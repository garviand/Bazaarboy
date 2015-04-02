Bazaarboy.profile.channel =
    image:undefined
    init: () ->
        scope = this
        if imageId?
            scope.image = imageId
        $('input[name=end_date]').pikaday
            format: 'MM/DD/YYYY'
        $('a.create-sign-up-btn, a.save-sign-up-btn').click () ->
            params = {}
            if $(this).hasClass('create-sign-up-btn')
                targetUrl = 'lists/signup/create/'
            else
                targetUrl = 'lists/signup/save/'
                params.id = signupId
            if $('input[name=name]').val().trim() == ''
                swal 'You Must Add a Name'
                return
            params.name = $('input[name=name]').val()
            if $('textarea[name=description]').val().trim() == ''
                swal 'You Must Add a Description'
                return
            params.description = $('textarea[name=description]').val()
            if not moment($('input[name=end_date]').val(), 'MM/DD/YYYY').isValid()
                swal 'The End Date Format is Invalid (MM/DD/YYYY)'
                return
            params.end_time = moment($('input[name=end_date]').val(), 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss')
            if scope.image
                params.image = scope.image
            formattedFields = {}
            if $('input[name=extra_fields]').val().trim() isnt ''
                fields = $('input[name=extra_fields]').val().split(",")
                num = 0
                for field in fields
                    formattedFields[num] = field.trim()
                    num++
                params.extra_fields = JSON.stringify(formattedFields)
            Bazaarboy.post targetUrl, params, (response) ->
                if response.status is 'OK'
                    swal
                        type: 'success'
                        title: 'Success'
                        text: 'Sign Up Form Created!'
                        () ->
                            Bazaarboy.redirect 'lists/'
                else
                    swal response.message
                return
            return
        # cover image upload
        scope.aviary = new Aviary.Feather
            apiKey: 'ce3b87fb1edaa22c'
            apiVersion: 3
            enableCORS: true
            onSave: (imageId, imageUrl) =>
                $("img#cover-image").attr 'src', imageUrl
                scope.aviary.close();
                Bazaarboy.post 'file/aviary/profile/',
                    url: imageUrl
                , (response) ->
                    $("img#cover-image").attr 'src', response.image
                    $('a.upload-image-btn').css('display', 'none')
                    $('a.delete-image-btn').css('display', 'block')
                    $('a.upload-image-btn').html 'Upload Image'
                    scope.image = response.image_id
                    return
                return
        $('input[name=image_file]').fileupload
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                $('a.upload-cover-btn').html 'Uploading...'
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    $('img#cover-image').attr 'src', mediaUrl + response.image.source
                    scope.aviary.launch
                        image: 'cover-image'
                        url: mediaUrl + response.image.source
                        maxSize: 1260
                        cropPresetsStrict: true
                        cropPresetDefault: ['Cover Photo Size','1000x400']
                        initTool: 'crop'
                else
                    swal response.message
                    $('a.upload-cover-btn').html 'Upload Image'
                return
        $('a.upload-image-btn').click () ->
            $('input[name=image_file]').click()
            return
         $('a.delete-image-btn').click () ->
            scope.image = undefined
            $('img#cover-image').attr 'src', ''
            $('a.upload-cover-btn').css('display', 'block')
            $('a.delete-cover-btn').css('display', 'none')
            return
        return

Bazaarboy.profile.channel.init()