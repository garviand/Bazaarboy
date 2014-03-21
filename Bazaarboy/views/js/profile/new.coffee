Bazaarboy.profile.new =
    map: undefined
    marker: undefined
    coordinates: new google.maps.LatLng(38.650068, -90.259904)
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
    init: () ->
        scope = this
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
                    $('div.profile-new-container div.next-prev a').removeClass('hide')
                    if next_step == 1
                        $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide')
                    if next_step == $('div.profile-new-container div.profile-step-btn a').length
                        $('div.profile-new-container div.next-prev a.next-btn').addClass('hide')
                    step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title')
                    $('div.profile-new-container .title .step-title').html(step_title)
                    return
                return
            return
        $('div.profile-new-container div.next-prev a').click () ->
            active_button_container = $('div.profile-new-container div.profile-step-btn a.active').parent()
            if $(this).hasClass('prev-btn')
                next_active_button = active_button_container.prev().find('a')
            else
                next_active_button = active_button_container.next().find('a')
            next_step = next_active_button.data('id')
            $('div.profile-new-container div.next-prev a').removeClass('hide')
            if next_step == 1
                $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide')
            if next_step == $('div.profile-new-container div.profile-step-btn a').length
                $('div.profile-new-container div.next-prev a.next-btn').addClass('hide')
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
                    $('div.profile-new-container div.next-prev a').removeClass('hide')
                    if next_step == 1
                        $('div.profile-new-container div.next-prev a.prev-btn').addClass('hide')
                    if next_step == $('div.profile-new-container div.profile-step-btn a').length
                        $('div.profile-new-container div.next-prev a.next-btn').addClass('hide')
                    step_title = $('div.profile-new-container div.profile-step-' + next_step).data('title')
                    $('div.profile-new-container .title .step-title').html(step_title)
                    return
                return
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
            params = $(this).serializeObject()
            optionals = [
               'email', 'phone', 'link_website', 'link_facebook', 'EIN'
            ]
            params = Bazaarboy.stripEmpty params, optionals
            Bazaarboy.post 'profile/create/', params, (response) ->
                if response.status is 'OK'
                  Bazaarboy.redirect 'index'
                else
                  alert response.message
                return
            return
        # Location Auto-complete
        googleAutocomplete = new google.maps.places.AutocompleteService()
        $('form.profile-new input[name=location]').keyup () =>
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
                        $('form.profile-new input[name=location]').on 'autocompleteselect', (event, ui) =>
                            @fetchCoordinates ui.item.id
                            return
                        return
            return
        return

Bazaarboy.profile.new.init()