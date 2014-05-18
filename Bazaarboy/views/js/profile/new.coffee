Bazaarboy.profile.new =
    map: undefined
    marker: undefined
    coordinates: new google.maps.LatLng(38.650068, -90.259904)
    image: undefined
    uploads:
        image: undefined
    to_stripe: false
    fetchCoordinates: (reference) ->
        gmap = $('div#map-canvas-hidden').get(0)
        location = $('form.profile-new input[name=location]').val()
        placesService = new google.maps.places.PlacesService gmap
        placesService.getDetails
            reference: reference
        , (result, status) =>
            if status is 'OK'
                $('form.profile-new input[name=latitude]')
                    .val result.geometry.location.lat()
                $('form.profile-new input[name=longitude]')
                    .val result.geometry.location.lng()
                center = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng())
                @coordinates = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng())
                @map.panTo(center)
                @marker.setPosition(center)
            return
        return
    startEditingLogoImage: () ->
        scope = this
        $('<img>')
            .attr('src', mediaUrl + @uploads.image.source)
            .load () ->
                $('div.profile-new-container div.logo div.logo_image')
                    .html('')
                $('div.profile-new-container div.logo div.logo_image')
                    .append(this)
                $('div.profile-new-container div.logo a.upload')
                    .addClass('hide')
                $('div.profile-new-container div.logo a.cancel')
                    .removeClass('hide')
                return
        return
    stopEditingLogoImage: () ->
        @uploads.image = undefined
        @image = undefined
        $('div.profile-new-container div.logo div.logo_image').html('')
        $('div.profile-new-container div.logo a.upload')
            .removeClass('hide')
        $('div.profile-new-container div.logo a.cancel')
            .addClass('hide')
        return
    init: () ->
        scope = this
        $('div.profile-new-container div.logo a.upload').click () ->
            $('div#wrapper-profile-new form.upload_logo input[name=image_file]').click()
            return
        $('div.profile-new-container div.logo a.cancel').click () ->
            scope.stopEditingLogoImage()
            return
        $('div#wrapper-profile-new form.upload_logo input[name=image_file]').fileupload
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
        $('div.profile-new-container div.profile-step-btn a').click () ->
            $('div.profile-new-container div.profile-step-btn a').removeClass('active')
            $(this).addClass('active')
            next_step = $(this).data('id')
            $('div.profile-new-container div.profile-step.active').fadeOut 300, () ->
                $('div.profile-new-container .title .step-title').html('')
                $(this).removeClass('active')
                $('div.profile-new-container div.profile-step-' + next_step).addClass('active')
                $('div.profile-new-container div.profile-step-' + next_step).fadeIn 300, () ->
                    google.maps.event.trigger(scope.map, 'resize')
                    scope.map.setCenter(scope.coordinates)
                    $('div.profile-new-container div.next-prev a').not('.finish-btn').removeClass('hide')
                    if next_step == 1
                        $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide')
                    if next_step == $('div.profile-new-container div.profile-step-btn a').length
                        $('div.profile-new-container div.next-prev a.next-btn').addClass('hide')
                        $('div.profile-new-container div.next-prev a.finish-btn').removeClass('hide')
                    else
                        $('div.profile-new-container div.next-prev a.finish-btn').addClass('hide')
                    step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title')
                    $('div.profile-new-container .title .step-title').html(step_title)
                    return
                return
            return
        $('div.profile-new-container div.next-prev a').not('.finish-btn').click () ->
            active_button_container = $('div.profile-new-container div.profile-step-btn a.active').parent()
            if $(this).hasClass('prev-btn')
                next_active_button = active_button_container.prev().find('a')
            else
                next_active_button = active_button_container.next().find('a')
            next_step = next_active_button.data('id')
            $('div.profile-new-container div.next-prev a').not('.finish-btn').removeClass('hide')
            if next_step == 1
                $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide')
            if next_step == $('div.profile-new-container div.profile-step-btn a').length
                $('div.profile-new-container div.next-prev a.next-btn').addClass('hide')
            else
                $('div.profile-new-container div.next-prev a.finish-btn').addClass('hide')
            next_active_button.addClass('active')
            $('div.profile-new-container div.profile-step-btn a').removeClass('active')
            next_active_button.addClass('active')
            $('div.profile-new-container div.profile-step.active').fadeOut 300, () ->
                $('div.profile-new-container .title .step-title').html('')
                $(this).removeClass('active')
                $('div.profile-new-container div.profile-step-' + next_step).addClass('active')
                $('div.profile-new-container div.profile-step-' + next_step).fadeIn 300, () ->
                    google.maps.event.trigger(scope.map, 'resize')
                    scope.map.setCenter(scope.coordinates)
                    $('div.profile-new-container div.next-prev a').not('.finish-btn').removeClass('hide')
                    if next_step == 1
                        $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide')
                    if next_step == $('div.profile-new-container div.profile-step-btn a').length
                        $('div.profile-new-container div.next-prev a.next-btn').addClass('hide')
                        $('div.profile-new-container div.next-prev a.finish-btn').removeClass('hide')
                    else
                        $('div.profile-new-container div.next-prev a.finish-btn').addClass('hide')
                    step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title')
                    $('div.profile-new-container .title .step-title').html(step_title)
                    return
                return
            return
        $('div.profile-new-container a.stripe_connect').click (e) ->
            e.preventDefault()
            scope.to_stripe = true
            $('form.profile-new').submit()
            return
        $('div.profile-new-container div.next-prev .finish-btn').click () ->
            scope.to_stripe = false
            $('form.profile-new').submit()
            return
        $('div.profile-new-container input[name=is_non_profit]').change () ->
            if $(this).is(":checked")
                $('div.profile-new-container .ein').removeClass('hide')
            else
                $('div.profile-new-container .ein').addClass('hide')
            return
        # Initialize Map
        map_center = @coordinates
        mapOptions =
            zoom: 15
            center: map_center
        @map = new google.maps.Map document.getElementById('map-canvas'), mapOptions
        @marker = new google.maps.Marker(
            position: map_center
            map: @map
            draggable: true
        )
        google.maps.event.addListener @marker, 'drag', () =>
            $('form.profile-new input[name=latitude]').val(@marker.position.lat())
            $('form.profile-new input[name=longitude]').val(@marker.position.lng())
            @coordinates = new google.maps.LatLng(@marker.position.lat(), @marker.position.lng())
            return
        $('form.profile-new').submit (event) ->
            event.preventDefault()
            return
        # Location Auto-complete
        googleAutocomplete = new google.maps.places.AutocompleteService()
        $('form.profile-new input[name=location]').keypress () =>
            keyword = $('form.profile-new input[name=location]').val()
            if keyword.trim() isnt ''
                googleAutocomplete.getQueryPredictions
                    types: ['establishment']
                    input: keyword
                , (predictions, status) =>
                    autocompleteSource = []
                    if predictions and predictions.length > 0
                        for prediction in predictions
                            if prediction['terms'].length > 2
                                labelExtenstion = ' - <i>' + prediction['terms'][2]['value'] + '</i>'
                            else
                                labelExtenstion = ''
                            autocompleteSource.push
                                id: prediction['reference']
                                value: prediction['terms'][0]['value']
                                label: prediction['terms'][0]['value'] + labelExtenstion
                        $('form.profile-new input[name=location]').autocomplete
                            source: autocompleteSource
                            html: true
                            matchContains: true
                            minChars: 0
                        $('form.profile-new input[name=location]').autocomplete("search"," ")
                        $('form.profile-new input[name=location]').on 'autocompleteselect', (event, ui) =>
                            @fetchCoordinates ui.item.id
                            return
                        return
            return
        $('form.profile-new').on 'invalid', () ->
            invalid_fields = $(this).find('[data-invalid]')
            invalid_step = $(invalid_fields[0]).parents('.profile-step').data('id')
            $('form.profile-new .profile-step-btn-' + invalid_step + ' a').click()
            return
        $('form.profile-new').on 'valid', () ->
            params = $(this).serializeObject()
            optionals = [
               'phone', 'link_website', 'link_facebook', 'EIN', 'latitude', 'longitude'
            ]
            params = Bazaarboy.stripEmpty params, optionals
            if typeof scope.uploads.image != 'undefined'
                params.image = scope.uploads.image.pk
            if $('form.profile-new input[name=is_non_profit]').is(':checked') and $('form.profile-new input[name=EIN]').val().trim().length > 0
                params.is_non_profit = true
            else
                params.is_non_profit = false
            Bazaarboy.post 'profile/create/', params, (response) ->
                if response.status is 'OK'
                    if scope.to_stripe
                        window.location = $('div.profile-new-container a.stripe_connect').attr('href')
                    else
                        Bazaarboy.redirect 'index'
                else
                    alert response.message
                return
            return
        return

Bazaarboy.profile.new.init()