Bazaarboy.event.index = 
    description: undefined
    map: undefined
    cover: undefined
    uploads:
        cover: undefined
    coverEditInProgress: false
    drawMapWithCenter: (latitude, longitude) ->
        center = new google.maps.LatLng(latitude + 0.0015, longitude)
        mapOpts = 
            center: center
            zoom: 14
            mapTypeId: google.maps.MapTypeId.ROADMAP
            draggable: false
            mapTypeControl: false
            overviewMapControl: false
            streetViewControl: false
            scaleControl: false
            zoomControl: false
        canvas = document.getElementById('map_canvas')
        @map = new google.maps.Map(canvas, mapOpts)
        markerPos = new google.maps.LatLng(latitude, longitude)
        marker = new google.maps.Marker({position: markerPos})
        marker.setMap @map
        return
    initTransaction: () ->
        # Account control
        $('div#rsvp form.login').submit (event) ->
            event.preventDefault()
            Bazaarboy.get 'user/auth/', $(this).serializeObject()
            , (response) ->
                if response.status is 'OK'
                    window.location.hash = '#rsvp'
                    window.location.reload()
                else
                    console.log response
                return
            return
        $('div#rsvp form.register').submit (event) ->
            event.preventDefault()
            Bazaarboy.post 'user/create/', $(this).serializeObject()
            , (response) ->
                if response.status is 'OK'
                    window.location.hash = '#rsvp'
                    window.location.reload()
                else
                    console.log response
                return
            return
        $('div#rsvp form.register').submit (event) ->
            event.preventDefault()
            return
        # Check whether to open the RSVP modal
        if window.location.hash? and window.location.hash is '#rsvp' and editable
            $('div#event div.action').click()
        return
    save: (params, cb) ->
        params.id = eventId
        if token?
            params.token = token
        Bazaarboy.post 'event/edit/', params, (response) ->
            if response.status is 'OK'
                return cb null, response.event
            else
                err = 
                    error: response.error
                    message: response.message
                return cb err, null
            return
        return
    prepareUploadedCoverImage: (coverUrl) ->
        if not $('body').hasClass('collapsed')
            Bazaarboy.switchCollapsedStates () =>
                @prepareUploadedCoverImage(coverUrl)
                return
            return
        $('div#event').addClass('big_cover').addClass('with_caption')
        scope = this
        $('<img>')
            .attr('src', mediaUrl + coverUrl)
            .addClass('editing')
            .load () ->
                scope.uploads.cover.width = @width
                scope.uploads.cover.height = @height
                # Adjust the size of the image to fill the frame
                frame = $('div#event div.cover div.image')
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
        @coverEditInProgress = true
        # Set up the draggable boundaries
        frame = $('div#event div.cover div.image')
        coverImage = $('div#event div.cover div.image img')
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
        $('div#event div.cover div.controls span').removeClass('hidden')
        $('div#event div.cover div.controls a.edit')
            .addClass('hidden')
            .html('Edit Cover')
            $('div#event div.cover div.controls a.delete').addClass('hidden')
        $('div#event div.cover div.controls a.save').removeClass('hidden')
        $('div#event div.cover div.controls a.cancel').removeClass('hidden')
        # Create the expose effect
        maskZ = parseInt($('div#wrapper_overlay').css('z-index'))
        $('div#event div.cover').css
            'z-index': maskZ + 1
        $('div#event > div.title').css
            'z-index': maskZ + parseInt($('div#event > div.title')
                                        .css('z-index'))
        $('div#event div.frame div.right div.info')
            .not('div.action').not('div.details').not('div.facebook')
            .css('z-index', maskZ - 1)
        $('div#wrapper_overlay').fadeIn(200)
        $('div#event div.cover div.controls').addClass('stick')
        return
    stopEditingCoverImage: (cover=null) ->
        # Destroy the image and restore the bounds
        $('div#event div.cover div.image div.bounds img').remove()
        $('div#event div.cover div.image div.bounds')
            .css
                width: ''
                height: ''
                top: ''
                left: ''
        # Replace the cover
        if cover?
            if cover
                $('div#event div.cover div.image div.bounds').append(cover)
            else
                $('div#event').removeClass('with_caption').removeClass('big_cover')
                $('div#event div.cover div.controls').addClass('stick')
                $('div#event div.cover div.controls a.edit')
                    .html('Add Cover')
        # Restore z-indices
        $('div#event div.cover').css 'z-index', ''
        $('div#event > div.title').css 'z-index', ''
        $('div#event div.frame div.right div.info')
            .not('div.action').not('div.details').not('div.facebook')
            .css('z-index', '')
        $('div#wrapper_overlay').fadeOut(200)
        # Adjust the controls
        $('div#event div.cover div.controls span').addClass('hidden')
        $('div#event div.cover div.controls a.edit').removeClass('hidden')
        $('div#event div.cover div.controls a.delete').removeClass('hidden')
        $('div#event div.cover div.controls a.save').addClass('hidden')
        $('div#event div.cover div.controls a.cancel').addClass('hidden')
        $('div#event div.cover div.controls').removeClass('stick')
        @coverEditInProgress = false
        return
    saveCoverImage: () ->
        # Get the viewport of the image
        frame = $('div#event div.cover div.image')
        bounds = $('div#event div.cover div.image div.bounds')
        coverImage = $('div#event div.cover div.image div.bounds img')
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
                @save {cover: response.image.pk}, (err, event) =>
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
        @save {cover: 'delete'}, (err, event) =>
            unless err
                $('div#event div.cover div.image div.bounds img').remove()
                $('div#event div.cover div.controls a.edit').html('Add Cover')
                $('div#event div.cover div.controls a.delete').addClass('hidden')
                $('div#event div.cover div.controls').addClass('stick')
                $('div#event').removeClass('big_cover').removeClass('with_caption')
                @cover = null
            else
                alert err.message
            return
    startEditingDescription: () ->
        $('div.description div.controls a.edit').html('Cancel')
        $('div.description div.controls a.save').show()
        $('div.description div.editor').addClass('editing')
        $('div.description div.editor div.inner').redactor
            buttons: [
                'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                'alignment', '|',
                'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                'image', 'video', 'link', '|',
                'html'
            ]
            boldTag: 'b'
            italicTag: 'i'
        return
    stopEditingDescription: (description) ->
        $('div.description div.controls a.edit').html('Edit')
        $('div.description div.controls a.save').hide()
        $('div.description div.editor').removeClass('editing')
        $('div.description div.editor div.inner').redactor('destroy')
        $('div.description div.editor div.inner').html(description)
        return
    saveDescription: () ->
        description = $('div.description div.editor div.inner').redactor('get')
        @save {description: description}, (err, event) =>
            unless err
                @description = event.description
                @stopEditingDescription @description
            else
                alert err.message
            return
        return
    startEditingSummary: () ->
        $('div#event div.summary div.body div.text').addClass('hidden')
        $('div#event div.right div.summary div.editor').removeClass('hidden')
        $('div#event div.right div.summary div.button')
            .html('Save')
            .addClass('stick')
        return
    stopEditingSummary: () ->
        summary = $('div#event div.summary div.editor textarea').val().trim()
        @save {summary: summary}, (err, event) =>
            unless err
                summaryText = summary
                if summary.length is 0
                    summaryText = '<i>No summary yet.</i>'
                $('div#event div.summary div.body div.text')
                    .html(summaryText)
                    .removeClass('hidden')
                $('div#event div.summary div.editor textarea').val(summary)
                $('div#event div.summary div.editor').addClass('hidden')
                $('div#event div.summary div.button')
                    .html('Edit')
                    .removeClass('stick')
            else
                alert err.message
            return
        return
    startEditingTags: () ->
        $('div#event div.tags div.body div.text').addClass('hidden')
        $('div#event div.right div.tags div.editor').removeClass('hidden')
        $('div#event div.right div.tags div.button')
            .html('Save')
            .addClass('stick')
        return
    stopEditingTags: () ->
        tags = $('div#event div.tags div.editor textarea').val().trim()
        @save {tags: tags}, (err, event) =>
            unless err
                $('div#event div.tags div.editor textarea').val(tags)
                tagsText = '<i>No tags yet.</i>'
                if tags.length isnt 0
                    tagsText = ''
                    tags = tags.split(',')
                    for tag in tags
                        tagsText += "<div class=\"tag\">#{tag}</div>"
                    tagsText += '<div class="clear"></div>'
                $('div#event div.tags div.body div.text')
                    .html(tagsText)
                    .removeClass('hidden')
                $('div#event div.tags div.editor').addClass('hidden')
                $('div#event div.tags div.button')
                    .html('Edit')
                    .removeClass('stick')
            else
                alert err.message
            return
        return
    initEditing: () ->
        # Save original images
        @cover = $('div#event div.cover div.image div.bounds img')
        if @cover.length > 0
            @cover = @cover.clone()
        # Image uploads
        $('div#event div.cover a.edit').click () ->
            $('div#event div.cover input[name=image_file]').click()
            return
        $('div#event div.cover a.delete').click () =>
            if confirm('Are you sure you want to delete the cover image?')
                @deleteCoverImage()
            return
        $('div#event div.cover a.save').click () =>
            @saveCoverImage()
            return
        $('div#event div.cover a.cancel').click () =>
            original = if @cover? then @cover else false
            @stopEditingCoverImage(original)
            if @uploads.cover?
                Bazaarboy.post 'file/image/delete/', 
                    id: @uploads.cover.pk
                , (response) =>
                    @uploads.cover = null
            return
        $('div#event div.cover input[name=image_file]').fileupload 
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
        return
        # Edit description
        @description = $('div#event div.description div.inner').html()
        $('div#event div.description div.controls a.save').hide().click () =>
            @saveDescription()
        $('div#event div.description div.controls a.edit').click () =>
            if $('div.description div.editor').hasClass('editing')
                @stopEditingDescription @description
            else
                @startEditingDescription()
            return
        # Edit summary
        scope = this
        $('div#event div.summary div.button').click () ->
            if $(this).hasClass('stick')
                scope.stopEditingSummary()
            else
                scope.startEditingSummary()
            return
        # Edit tags
        $('div#event div.tags div.button').click () ->
            if $(this).hasClass('stick')
                scope.stopEditingTags()
            else
                scope.startEditingTags()
            return
        return
    init: () ->
        # Extend collapse animations
        collapseStates = [
            ['div#event', [['margin-left', '63px', '96px']]]
            ['div#event.big_cover div.cover', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#event > div.title', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#event > div.title div.text', [['left', '63px', '96px']]]
        ]
        $.merge(Bazaarboy.collapseStates, collapseStates)
        # Overlay
        $('div#event div.action').click () ->
            $('div#wrapper_overlay').fadeIn(200)
            $('div.event_overlay_canvas').fadeIn(200)
            return
        $('div#wrapper_overlay').click () =>
            if not @coverEditInProgress
                $('div#wrapper_overlay').fadeOut(200)
                $('div.event_overlay_canvas').fadeOut(200)
            return
        # Maps
        ###
        latitude = parseFloat $('div#event div.details div.map').attr('data-latitude')
        longitude = parseFloat $('div#event div.details div.map').attr('data-longitude')
        if latitude isnt NaN and longitude isnt NaN
            @drawMapWithCenter latitude, longitude
        ###
        # Further initialization
        if editable then @initEditing() else @initTransaction()
        return

Bazaarboy.event.index.init()