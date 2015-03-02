Bazaarboy.event.invite =
    saving: false
    image: {}
    init: () ->
        scope = this
        if imgId?
            scope.image = {pk:imgId}
        #NEW LIST
        $(".new-list-btn").click () ->
            $("div#new-list-modal").foundation('reveal', 'open')
            return
        $("a.close-list-modal").click () ->
            $("div#new-list-modal").foundation('reveal', 'close')
            return
        $("div#new-list-modal div.new-list-inputs a.create-list").click () ->
            $(this).html 'Creating...'
            list_name = $("div#new-list-modal div.new-list-inputs input[name=list_name]").val()
            if list_name.trim() isnt ''
                Bazaarboy.post 'lists/create/', {profile:profileId, name:list_name, is_hidden:1}, (response) ->
                    if response.status is 'OK'
                        Bazaarboy.redirect 'lists/' + response.list.pk
                    return
            else
                alert 'List name can\'t be empty'
            return
        # SELECT LISTS
        $('div.lists div.list').click () ->
            $(this).toggleClass 'active'
            return
        # LOGO UPLOAD
        scope.aviary = new Aviary.Feather
            apiKey: 'ce3b87fb1edaa22c'
            apiVersion: 3
            enableCORS: true
            onSave: (imageId, imageUrl) =>
                $("img#header-image").attr 'src', imageUrl
                scope.aviary.close();
                console.log imageUrl
                $('a.upload-logo-btn').html 'Uploading...'
                Bazaarboy.post 'file/aviary/profile/',
                    url: imageUrl
                    , (response) ->
                        console.log response
                        $("img#header-image").attr 'src', response.image
                        scope.image.pk = response.image_id
                        $('div#event-invite a.upload-image-btn').html 'Upload Image'
                        $('div#event-invite div.image-preview').removeClass 'hide'
                        $('div#event-invite a.upload-image-btn').css('display', 'none')
                        $('div#event-invite a.delete-image-btn').css('display', 'block')
                        return
                return
        # IMAGE UPLOAD
        $('div#event-invite a.upload-image-btn').click () ->
            $('div#event-invite input[name=image_file]').click()
            return
        $('div#event-invite a.delete-image-btn').click () ->
            scope.image = {}
            $('div#event-invite div.image-preview img').attr('src', '')
            $('div#event-invite div.image-preview').addClass 'hide'
            $('div#event-invite a.upload-image-btn').css('display', 'block')
            $('div#event-invite a.delete-image-btn').css('display', 'none')
            return
        $('div#event-invite input[name=image_file]').fileupload
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                $('div#event-invite a.upload-image-btn').html 'Uploading...'
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    $('img#header-image').attr 'src', mediaUrl + response.image.source
                    scope.aviary.launch
                        image: 'header-image'
                        url: mediaUrl + response.image.source
                else
                    swal response.message
                    $('div#event-invite a.upload-image-btn').html 'Upload Image'
                return
        # COLOR PICKER
        $('input[name=colorpicker]').spectrum
            preferredFormat: "hex"
            showInput: true
            showButtons: true
        # SAVE & PREVIEW
        $('a.save-invite').click () ->
            if not scope.saving
                $('a.save-invite').html 'Saving...'
                scope.saving = true
                if not inviteEdit
                    targetId = $('div.email input[name=event]').val()
                    targetUrl = 'event/invite/new/'
                else
                    targetId = $('div.email input[name=invite]').val()
                    targetUrl = 'event/invite/save/'
                message = $('div.email textarea[name=message]').val()
                if message.trim() is ''
                    swal("Wait!", "Email Message Cannot Be Empty", "warning")
                    scope.saving = false
                    $('a.save-invite').html 'Save &amp; Preview'
                    return
                details = $('div.email textarea[name=details]').val()
                activeLists = $('div.lists div.list.active')
                if activeLists.length is 0
                    swal("Wait!", "You Must Select At Least 1 List", "warning")
                    scope.saving = false
                    $('a.save-invite').html 'Save &amp; Preview'
                    return
                lists = ''
                for list in activeLists
                    if lists != ''
                        lists += ', '
                    lists += $(list).data('id')
                imageId = ''
                deleteImg = true
                if scope.image.pk?
                    imageId = scope.image.pk
                    deleteImg = false
                color = $('input[name=colorpicker]').spectrum("get").toHexString()
                Bazaarboy.post targetUrl, {id:targetId, message:message, details:details, lists:lists, image:imageId, color:color, deleteImg:deleteImg}, (response) ->
                    if response.status is 'OK'
                        inviteId = response.invite.pk
                        Bazaarboy.redirect 'event/invite/' + inviteId + '/preview'
                        return
                    scope.saving = false
                    $('a.save-invite').html 'Save &amp; Preview'
                    return
            return
        return
        
Bazaarboy.event.invite.init()