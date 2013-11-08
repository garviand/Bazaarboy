Bazaarboy.profile.index = 
    description: undefined
    image: undefined
    cover: undefined
    uploads:
        image: undefined
        cover: undefined
    switchTab: (tab) ->
        $('div#profile div.tabs div.tab').each () ->
            if $(this).hasClass(tab)
                $(this).addClass('show')
            else
                $(this).removeClass('show')
            return
        $('div#profile div.frame div.wrapper > div').each () ->
            if $(this).hasClass(tab)
                $(this).addClass('show')
            else
                $(this).removeClass('show')
            return
        return
    save: (params, cb) ->
        params.id = profileId
        Bazaarboy.post 'profile/edit/', params, (response) ->
            if response.status is 'OK'
                return cb null, response.profile
            else
                err = 
                    error: response.error
                    message: response.message
                return cb err, null
            return
        return
    prepareUploadedCoverImage: (coverUrl) ->
        scope = this
        $('<img>')
            .attr('src', mediaUrl + coverUrl)
            .addClass('editing')
            .load () ->
                scope.uploads.cover.width = @width
                scope.uploads.cover.height = @height
                # Adjust the size of the image to fill the frame
                frame = $('div#profile div.cover div.image')
                frameWidth = $(frame).width()
                frameHeight = $(frame).height()
                if @width / @height > frameWidth / frameHeight
                    $(this).height(frameHeight)
                    $(this).width(@width / @height * frameHeight)
                else
                    $(this).width(frameWidth)
                    $(this).height(@height / @width * frameWidth)
                $(frame).find('div.bounds').children().remove()
                $(frame).find('div.bounds').append(this)
                scope.startEditingCoverImage()
                return
        return
    startEditingCoverImage: () ->
        # Set up the draggable boundaries
        frame = $('div#profile div.cover div.image')
        coverImage = $('div#profile div.cover div.image img')
                         .css
                            top: 0
                            left: 0
        width = coverImage.width() * 2 - frame.width()
        height = coverImage.height() * 2 - frame.height()
        left = 0 - (width - frame.width()) / 2
        top = 0 - (height - frame.height()) / 2
        bounds = $(frame).find('div.bounds')
                         .css
                            width: width
                            height: height
                            top: top
                            left: left
        $(coverImage).draggable 
            containment: bounds
            scroll: false
        # Adjust the controls
        $('div#profile div.cover div.controls span').removeClass('hidden')
        $('div#profile div.cover div.controls a.edit')
            .addClass('hidden')
            .html('Edit Cover')
            $('div#profile div.cover div.controls a.delete').addClass('hidden')
        $('div#profile div.cover div.controls a.save').removeClass('hidden')
        $('div#profile div.cover div.controls a.cancel').removeClass('hidden')
        # Create the expose effect
        maskZ = parseInt($('div#wrapper_overlay').css('z-index'))
        $('div#profile div.cover').css
            'z-index': maskZ + 1
        $('div#profile > div.title').css
            'z-index': maskZ + parseInt($('div#profile > div.title')
                                        .css('z-index'))
        $('div#profile div.right div.image').css
            'z-index': maskZ + parseInt($('div#profile div.right div.image')
                                        .css('z-index'))
        $('div#profile div.right div.action').css
            'z-index': maskZ + parseInt($('div#profile div.right div.action')
                                        .css('z-index'))
        $('div#wrapper_overlay').fadeIn(200)
        $('div#profile div.cover div.controls').addClass('stick')
        return
    stopEditingCoverImage: (cover=null) ->
        # Destroy the image and restore the bounds
        $('div#profile div.cover div.image div.bounds img').remove()
        $('div#profile div.cover div.image div.bounds')
            .css
                width: ''
                height: ''
                top: ''
                left: ''
        # Replace the cover
        if cover?
            if cover
                $('div#profile div.cover div.image div.bounds').append(cover)
            else
                $('div#profile div.cover div.controls a.edit')
                    .html('Add Cover')
        # Restore z-indices
        $('div#profile div.cover').css 'z-index', ''
        $('div#profile > div.title').css 'z-index', ''
        $('div#profile div.right div.image').css 'z-index', ''
        $('div#profile div.right div.action').css 'z-index', ''
        $('div#wrapper_overlay').fadeOut(200)
        # Adjust the controls
        $('div#profile div.cover div.controls span').addClass('hidden')
        $('div#profile div.cover div.controls a.edit').removeClass('hidden')
        $('div#profile div.cover div.controls a.delete').removeClass('hidden')
        $('div#profile div.cover div.controls a.save').addClass('hidden')
        $('div#profile div.cover div.controls a.cancel').addClass('hidden')
        $('div#profile div.cover div.controls').removeClass('stick')
        return
    saveCoverImage: () ->
        # Get the viewport of the image
        frame = $('div#profile div.cover div.image')
        bounds = $('div#profile div.cover div.image div.bounds')
        coverImage = $('div#profile div.cover div.image div.bounds img')
        x = 0
        y = 0
        width = 0
        height = 0
        if coverImage.width() > frame.width()
            scale = @uploads.cover.height / frame.height()
            x = (Math.abs(parseInt($(bounds).css('left'))) - 
                parseInt(coverImage.css('left'))) * scale
            y = 0
            width = frame.width() * scale
            height = @uploads.cover.height
        else
            scale = @uploads.cover.width / frame.width()
            x = 0
            y = (Math.abs(parseInt($(bounds).css('top'))) - 
                parseInt(coverImage.css('top'))) * scale
            width = @uploads.cover.width
            height = frame.height() * scale
        x = parseInt(x)
        y = parseInt(y)
        width = parseInt(width)
        height = parseInt(height)
        viewport = "#{x},#{y},#{width},#{height}"
        console.log viewport
        Bazaarboy.post 'file/image/crop/', 
            id: @uploads.cover.pk
            viewport: viewport
        , (response) =>
            if response.status is 'OK'
                @save {cover: response.image.pk}, (err, profile) =>
                    unless err
                        @cover = response.image
                        @cover.width = width
                        @cover.height = height
                        @uploads.cover = null
                        scope = this
                        $('<img>')
                            .attr('src', mediaUrl + response.image.source)
                            .addClass('normal')
                            .load () ->
                                scope.stopEditingCoverImage(this)
                                return
                    else
                        alert err.message
                    return
            else
                alert response.message
            return
        return
    deleteCoverImage: () ->
        @save {cover: 'delete'}, (err, profile) =>
            unless err
                $('div#profile div.cover div.image div.bounds img').remove()
                $('div#profile div.cover div.controls a.edit').html('Add Cover')
                $('div#profile div.cover div.controls a.delete').addClass('hidden')
                @cover = null
            else
                alert err.message
            return
    startEditingDescription: () ->
        $('div.overview div.description div.controls a.edit').html('Cancel')
        $('div.overview div.description div.controls a.save').show()
        $('div.overview div.description div.editor').addClass('editing')
        $('div.overview div.description div.editor div.inner').redactor
            buttons: [
                'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                'alignment', '|',
                'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                'image', 'video', 'link'
            ]
            imageUpload: rootUrl
        return
    stopEditingDescription: (description) ->
        $('div.overview div.description div.controls a.edit').html('Edit')
        $('div.overview div.description div.controls a.save').hide()
        $('div.overview div.description div.editor').removeClass('editing')
        $('div.overview div.description div.editor div.inner').redactor('destroy')
        $('div.overview div.description div.editor div.inner').html(description)
        return
    saveDescription: () ->
        description = $('div.overview div.description div.editor div.inner')
                      .redactor('get')
        @save {description: description}, (err, profile) =>
            unless err
                @description = profile.description
                @stopEditingDescription @description
            else
                alert err.message
            return
        return
    startEditingLogoImage: () ->
        scope = this
        $('<img>')
            .attr('src', mediaUrl + @uploads.image.source)
            .load () ->
                $('div#profile div.frame div.right div.logo div.image')
                    .html('')
                $('div#profile div.frame div.right div.logo div.image')
                    .append(this)
                $('div#profile div.frame div.right div.logo a.upload')
                    .addClass('hidden')
                $('div#profile div.frame div.right div.logo a.delete')
                    .addClass('hidden')
                $('div#profile div.frame div.right div.logo a.save')
                    .removeClass('hidden')
                $('div#profile div.frame div.right div.logo a.cancel')
                    .removeClass('hidden')
                return
        return
    saveLogoImage: () ->
        @save {image: @uploads.image.pk}, (err, profile) =>
            unless err
                @uploads.image = null
                @stopEditingLogoImage()
            else
                alert err.message
            return
        return
    stopEditingLogoImage: () ->
        $('div#profile div.frame div.right div.logo a.upload')
            .removeClass('hidden')
        $('div#profile div.frame div.right div.logo a.delete')
            .removeClass('hidden')
        $('div#profile div.frame div.right div.logo a.save')
            .addClass('hidden')
        $('div#profile div.frame div.right div.logo a.cancel')
            .addClass('hidden')
        return
    initEditing: () ->
        # Edit description
        @description = $('div.overview div.description div.inner').html()
        $('div.overview div.description div.controls a.save').hide().click () =>
            @saveDescription()
        $('div.overview div.description div.controls a.edit').click () =>
            if $('div.overview div.description div.editor').hasClass('editing')
                @stopEditingDescription @description
            else
                @startEditingDescription()
            return
        # Save original images
        @cover = $('div#profile div.cover div.image div.bounds img')
        if @cover.length > 0
            @cover = @cover.clone()
        # Image uploads
        $('div#profile div.cover a.edit').click () ->
            $('div#profile div.cover input[name=image_file]').click()
            return
        $('div#profile div.cover a.delete').click () =>
            if confirm('Are you sure you want to delete the cover image?')
                @deleteCoverImage()
            return
        $('div#profile div.cover a.save').click () =>
            @saveCoverImage()
            return
        $('div#profile div.cover a.cancel').click () =>
            original = if @cover? then @cover else false
            @stopEditingCoverImage(original)
            if @uploads.cover?
                Bazaarboy.post 'file/image/delete/', 
                    id: @uploads.cover.pk
                , (response) =>
                    @uploads.cover = null
            return
        $('div#profile div.cover input[name=image_file]').fileupload 
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    # Attempt to delete the last uploaded image
                    if @uploads.cover?
                        Bazaarboy.post 'file/image/delete/', 
                            id: @uploads.cover.pk
                    @uploads.cover = response.image
                    @prepareUploadedCoverImage(response.image.source)
                else
                    alert response.message
                return
        $('div#profile div.frame div.right div.logo a.upload').click () ->
            $('div#profile div.frame div.right input[name=image_file]').click()
            return
        $('div#profile div.frame div.right div.logo a.delete').click () ->
            return
        $('div#profile div.frame div.right div.logo a.save').click () =>
            @saveLogoImage()
            return
        $('div#profile div.frame div.right div.logo a.cancel').click () ->
            return
        $('div#profile div.frame div.right input[name=image_file]').fileupload
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    # Attempt to delete the last uploaded image
                    if @uploads.image?
                        Bazaarboy.post 'file/image/delete/', 
                            id: @uploads.image.pk
                    @uploads.image = response.image
                    @startEditingLogoImage()
                else
                    alert response.message
                return
        return
    init: () ->
        # Tabs
        $.each ['overview', 'events', 'sponsorships'], (index, tab) =>
            $('div.tabs div.tab.' + tab).click () =>
                @switchTab tab
                return
            return
        # Further initialization
        if editable then @initEditing()
        return

Bazaarboy.profile.index.init()