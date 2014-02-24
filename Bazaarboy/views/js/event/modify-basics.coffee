Bazaarboy.event.modify.basics =
    isEditing: false
    map: undefined
    marker: undefined
    save: (params, cb) ->
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
    saveBasics: (auto_save) ->
        save_data = $('form.event-modify').serializeObject()
        console.log save_data
        if save_data.name.length > 150
            console.log('Name is too long.')
        if save_data.summary.length > 250
            console.log('Summary is too long.')
        if save_data.start_date.trim().length != 0 and save_data.start_time.trim().length != 0 and moment(save_data.start_date, 'MM/DD/YYYY').isValid() and moment(save_data.start_time, 'h:mm a').isValid()
            start_time = moment(save_data.start_date + ' ' + save_data.start_time, 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss')
        else
            start_time = ''
        if save_data.end_date.trim().length is 0 or save_data.end_time.trim().length is 0
            end_time = false
        else
            if not moment(save_data.end_date, 'MM/DD/YYYY').isValid()
                return
            if not moment(save_data.end_time, 'h:mm a').isValid()
                return
            end_time = moment(save_data.end_date + ' ' + save_data.end_time, 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss')
        @save
            id: eventId
            start_time: start_time
            end_time: if end_time then end_time else 'none'
            name: save_data.name
            summary: save_data.summary
            location: save_data.location
            latitude: save_data.latitude
            longitude: save_data.longitude
        , (err, event) =>
            unless err
                console.log 'Saved'
                if not auto_save
                    window.location = '/event/' + eventId + '/design'
            else
                console.log err
            return
        return
    autoSave: () ->
        if not @isEditing
            @saveBasics(true)
        return
    fetchCoordinates: (reference) ->
        gmap = $('div#map-canvas-hidden').get(0)
        location = $('form.event-modify input[name=location]').val()
        placesService = new google.maps.places.PlacesService gmap
        placesService.getDetails
            reference: reference
        , (result, status) =>
            if status is 'OK'
                $('form.event-modify input[name=latitude]')
                    .val result.geometry.location.lat()
                $('form.event-modify input[name=longitude]')
                    .val result.geometry.location.lng()
                center = new google.maps.LatLng(result.geometry.location.lat(), result.geometry.location.lng())
                @map.panTo(center)
                @marker.setPosition(center)
            return
        return
    init: () ->
        # Submit Form
        $('form.event-modify').submit (e) =>
            e.preventDefault()
            @saveBasics(false)
            return
        # Initialize Map
        initial_lat = $('form.event-modify input[name=latitude]').val()
        initial_lng = $('form.event-modify input[name=longitude]').val()
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
            $('form.event-modify input[name=latitude]').val(@marker.position.lat())
            $('form.event-modify input[name=longitude]').val(@marker.position.lng())
            return
        # Is User Editing Info
        $('form.event-modify').find('input, textarea').keyup () =>
            @isEditing = true
            setTimeout (() =>
                @isEditing = false
                return
            ), 5000
            return
        # Auto-save timer
        setInterval (() =>
            @autoSave()
            return
        ), 5000
        # Time auto-complete
        originalStartTime = $('form.event-modify input[name=start_time]').val()
        originalEndTime = $('form.event-modify input[name=end_time]').val()
        console.log $('form.event-modify input[name=start_time], form.event-modify input[name=end_time]').timeAutocomplete
            blur_empty_populate: false
            appendTo: '#menu-container'
        $('form.event-modify input[name=start_time]').val originalStartTime
        $('form.event-modify input[name=end_time]').val originalEndTime
        # Date auto-complete
        $('form.event-modify input[name=start_date]').pikaday
            format: 'MM/DD/YYYY'
            onSelect: () ->
                $('form.event-modify input[name=end_date]').pikaday 'gotoDate', this.getDate()
                $('form.event-modify input[name=end_date]').pikaday 'setMinDate', this.getDate()
                return
        $('form.event-modify input[name=end_date]').pikaday
            format: 'MM/DD/YYYY'
        # Location Auto-complete
        googleAutocomplete = new google.maps.places.AutocompleteService()
        $('form.event-modify input[name=location]').keyup () =>
            keyword = $('form.event-modify input[name=location]').val()
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
                        $('form.event-modify input[name=location]').autocomplete
                            source: autocompleteSource
                            html: true
                        $('form.event-modify input[name=location]').on 'autocompleteselect', (event, ui) =>
                            @fetchCoordinates ui.item.id
                            return
                        return
            return
        return

Bazaarboy.event.modify.basics.init()