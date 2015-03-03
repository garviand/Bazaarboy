Bazaarboy.profile.channel =
    image:imageId
    init: () ->
        scope = this
        # create channel
        $('a.create-channel-btn').click () ->
            params = {}
            params.profile = profileId
            if $('input[name=tagline]').val().trim() == ''
                swal 'You Must Add a Tagline'
                return
            params.tagline = $('input[name=tagline]').val()
            if $('input[name=hashtag]').val().trim() != ''
                params.hashtag = $('input[name=hashtag]').val()
            if not scope.image?
                swal 'You Must Upload A Cover Image'
                return
            params.cover = scope.image
            Bazaarboy.post 'profile/channel/create/', params, (response) ->
                if response.status is 'OK'
                    swal
                        type: 'success'
                        title: 'Success'
                        text: 'Channel Created!'
                        () ->
                            location.reload()
                else
                    swal response.message
                return
            return
        # edit channel
        $('a.save-channel-btn').click () ->
            params = {}
            params.profile = profileId
            if $('input[name=tagline]').val().trim() != ''
                params.tagline = $('input[name=tagline]').val()
            if $('input[name=hashtag]').val().trim() != ''
                params.hashtag = $('input[name=hashtag]').val()
            if scope.image?
                params.cover = scope.image
            Bazaarboy.post 'profile/channel/edit/', params, (response) ->
                if response.status is 'OK'
                    swal
                        type: 'success'
                        title: 'Success'
                        text: 'Channel Saved!'
                        () ->
                            location.reload()
                else
                    swal response.message
                return
            return
        # input interactions
        $('div.input-container').click () ->
            $(this).find('input, textarea').focus()
            return
        $('div.input-container input,div.input-container textarea').focus () ->
            $(this).closest('div.input-container').addClass 'active'
            return
        $('div.input-container input,div.input-container textarea').blur () ->
            $(this).closest('div.input-container').removeClass 'active'
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
                    $('a.upload-cover-btn').css('display', 'none')
                    $('a.delete-cover-btn').css('display', 'block')
                    $('a.upload-cover-btn').html 'Upload Image'
                    scope.image = (response.image_id)
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
                        maxSize: 1160
                        cropPresetsStrict: true
                        cropPresetDefault: ['Cover Photo Size','1000x400']
                        initTool: 'crop'
                else
                    swal response.message
                    $('a.upload-cover-btn').html 'Upload Image'
                return
        $('a.upload-cover-btn').click () ->
            $('input[name=image_file]').click()
            return
         $('a.delete-cover-btn').click () ->
            scope.image = undefined
            $('img#cover-image').attr 'src', ''
            $('a.upload-cover-btn').css('display', 'block')
            $('a.delete-cover-btn').css('display', 'none')
            return
        return

Bazaarboy.profile.channel.init()