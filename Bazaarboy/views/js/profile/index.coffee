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
        $('div#profile div.cover div.controls a.edit').html('Edit Cover')
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
    stopEditingCoverImage: (original=null) ->
        # Destroy the image if necessary
        if original?
            $('div#profile div.cover div.image div.bounds img').remove()
            if original
                $('div#profile div.cover div.image div.bounds').append(original)
            else
                $('div#profile div.cover div.controls a.edit')
                    .html('Add Cover')
        else
            # Or remove the draggable
            $('div#profile div.cover div.image img').draggable('destroy')
        # Restore z-indices
        $('div#profile div.cover').css 'z-index', ''
        $('div#profile > div.title').css 'z-index', ''
        $('div#profile div.right div.image').css 'z-index', ''
        $('div#profile div.right div.action').css 'z-index', ''
        $('div#wrapper_overlay').fadeOut(200)
        # Adjust the controls
        $('div#profile div.cover div.controls span').addClass('hidden')
        $('div#profile div.cover div.controls a.delete').addClass('hidden')
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
            console.log response
            #@stopEditingCoverImage()
            return
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
        @save {description: description}, (err, event) =>
            unless err
                @description = profile.description
                @stopEditingDescription @description
            else
                alert err.message
            return
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
        return
    init: () ->
        # Extend collapse animations
        collapseStates = [
            ['div#profile', [['margin-left', '63px', '96px']]]
            ['div#profile div.cover', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#profile > div.title', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#profile > div.title div.text', [['left', '63px', '96px']]]
            ['div#profile > div.tabs', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#profile > div.tabs div.inner', [['left', '63px', '96px']]]
        ]
        $.merge(Bazaarboy.collapseStates, collapseStates)
        # Tabs
        $.each ['overview', 'events', 'sponsorships'], (index, tab) =>
            $('div.tabs div.tab.' + tab).click () =>
                @switchTab tab
                return
            return
        # Save original images
        @image = $('div#profile div.right div.image img')
        if @image.length > 0
            @image = @image.clone()
        @cover = $('div#profile div.cover div.image div.bounds img')
        if @cover.length > 0
            @cover = @cover.clone()
        # Image uploads
        $('div#profile div.cover a.edit').click () ->
            $('div#profile div.cover input[name=image_file]').click()
            return
        $('div#profile div.cover a.save').click () =>
            @saveCoverImage()
            return
        $('div#profile div.cover a.cancel').click () =>
            original = if @cover? @cover else false
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
                    scope = this
                    $('<img>')
                        .attr('src', mediaUrl + response.image.source)
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
                else
                    alert response.message
                return
        # Further initialization
        if editable then @initEditing()
        return

Bazaarboy.profile.index.init()