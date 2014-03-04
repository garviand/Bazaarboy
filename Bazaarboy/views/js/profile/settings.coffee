Bazaarboy.event.modify.basics =
    isEditing: false
    map: undefined
    marker: undefined
    save: (params, cb) ->
        if token?
            params.token = token
        Bazaarboy.post 'profile/edit/', params, (response) ->
            if response.status is 'OK'
                return cb null, response.event
            else
                err = 
                    error: response.error
                    message: response.message
                return cb err, null
            return
        return
    saveSettings: (autoSave) ->
        save_data = $('form.profile-settings').serializeObject()
        if save_data.name.length > 100
            console.log('Name is too long.')
        $('div#profile-settings div.status').html 'Saving...'
        @save
            id: profileId
            name: save_data.name
            description: save_data.description
            location: save_data.location
            latitude: save_data.latitude
            longitude: save_data.longitude
        , (err, event) =>
            unless err
                setTimeout (() ->
                    $('div#profile-settings div.status').html 'Saved'
                    return
                ), 1000
            else
                $('div#profile-settings div.status').html 'Failed to save'
                console.log err
            return
        return
    autoSave: () ->
        if not @isEditing
            @saveSettings(true)
        return
    fetchCoordinates: (reference) ->
        gmap = $('div#map-canvas-hidden').get(0)
        location = $('form.profile-settings input[name=location]').val()
        placesService = new google.maps.places.PlacesService gmap
        placesService.getDetails
            reference: reference
        , (result, status) =>
            if status is 'OK'
                $('form.profile-settings input[name=latitude]')
                    .val result.geometry.location.lat()
                $('form.profile-settings input[name=longitude]')
                    .val result.geometry.location.lng()
                center = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng())
                @map.panTo(center)
                @marker.setPosition(center)
            return
        return
    init: () ->
        # Submit Form
        $('form.profile-settings').submit (e) =>
            e.preventDefault()
            @saveSettings(false)
            return
        # Initialize Map
        initial_lat = $('form.profile-settings input[name=latitude]').val()
        initial_lng = $('form.profile-settings input[name=longitude]').val()
        if initial_lat != 'None' and initial_lng != 'None'
            map_center = new google.maps.LatLng(initial_lat, initial_lng)
        else
            map_center = new google.maps.LatLng(38.650068, -90.259904)
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
            $('form.profile-settings input[name=latitude]').val(@marker.position.lat())
            $('form.profile-settings input[name=longitude]').val(@marker.position.lng())
            return
        # Is User Editing Info
        $('form.profile-settings').find('input, textarea').keyup () =>
            @isEditing = true
            $('div#profile-settings div.status').html 'Editing'
            setTimeout (() =>
                @isEditing = false
                return
            ), 5000
            return
        # Auto-save timer
        setInterval (() =>
            @autoSave()
            return
        ), 10000
        # Location Auto-complete
        googleAutocomplete = new google.maps.places.AutocompleteService()
        $('form.profile-settings input[name=location]').keyup () =>
            keyword = $('form.profile-settings input[name=location]').val()
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
                        $('form.profile-settings input[name=location]').autocomplete
                            source: autocompleteSource
                            html: true
                        $('form.profile-settings input[name=location]').on 'autocompleteselect', (event, ui) =>
                            @fetchCoordinates ui.item.id
                            return
                        return
            return
        return

Bazaarboy.event.modify.basics.init()