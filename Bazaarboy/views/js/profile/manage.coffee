Bazaarboy.profile.manage = 
    init: () ->
        $('form.create input[name=image_file]').fileupload
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (e, data) ->
                lastImgId = $('form.create input[name=image]').val()
                if lastImgId isnt ''
                    Bazaarboy.post 'file/image/delete/', {id: lastImgId}
                data.submit()
                return
            done: (e, data) ->
                result = jQuery.parseJSON(data.result)
                if result.status is 'OK'
                    $('form.create input[name=image]').val(result.image.pk)
                    imgUrl = mediaUrl + result.image.source
                    $('form.create img').attr('src', imgUrl)
                else
                    console.log result
                return
        return

Bazaarboy.profile.manage.init()