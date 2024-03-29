Bazaarboy.event.modify.basics =
    isEditing: false
    map: undefined
    marker: undefined
    autoSaveTimer: undefined
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
    saveBasics: (autoSave) ->
        save_data = $('form.event-modify').serializeObject()
        if save_data.name.length > 150
            console.log('Name is too long.')
        if save_data.summary.length > 250
            console.log('Summary is too long.')
        save_data.slug = save_data.slug.trim()
        if save_data.slug.length > 0
            if not /^[A-Za-z0-9-]{1,30}$/.test save_data.slug
                console.log('Invalid slug')
        else
            save_data.slug = 'None'
        if save_data.start_date.trim().length != 0 and save_data.start_time.trim().length != 0 and moment(save_data.start_date, 'MM/DD/YYYY').isValid() and moment(save_data.start_time, 'h:mm A').isValid()
            start_time = moment(save_data.start_date + ' ' + save_data.start_time, 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss')
        else
            start_time = ''
            $('div#event-modify-basics div.status').html 'Start Time is Invalid'
            return
        if save_data.end_date.trim().length is 0 or save_data.end_time.trim().length is 0
            end_time = false
        else
            if not moment(save_data.end_date, 'MM/DD/YYYY').isValid()
                $('div#event-modify-basics div.status').html 'End Time is Invalid'
                return
            if not moment(save_data.end_time, 'h:mm A').isValid()
                $('div#event-modify-basics div.status').html 'End Time is Invalid'
                return
            end_time = moment(save_data.end_date + ' ' + save_data.end_time, 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss')
        $('div#event-modify-basics div.status').html 'Saving...'
        @save
            id: eventId
            start_time: start_time
            end_time: if end_time then end_time else 'none'
            name: save_data.name
            summary: save_data.summary
            location: save_data.location
            latitude: save_data.latitude
            longitude: save_data.longitude
            slug: save_data.slug
        , (err, event) =>
            unless err
                setTimeout (() ->
                    $('div#event-modify-basics div.status').html 'Saved'
                    return
                ), 1000
                if not autoSave
                    window.location = '/event/' + eventId + '/tickets'
            else
                if err.error is 'DUPLICATE_SLUG' and not autoSave
                    $('div#event-modify-basics span.optional').addClass 'hide'
                    $('div#event-modify-basics span.taken').removeClass 'hide'
                    $('html, body').animate({scrollTop: $('div#event-modify-basics span.taken').offset().top - 100}, 1000);
                    setTimeout (() ->
                        $('div#event-modify-basics span.taken').addClass 'hide'
                        $('div#event-modify-basics span.optional').removeClass 'hide'
                        return
                    ), 4000
                else
                    $('div#event-modify-basics div.status').html err.message
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
        $('div.input-container').click () ->
            $(this).find('input, textarea').focus()
            return
        $('div.input-container input,div.input-container textarea').focus () ->
            $(this).closest('div.input-container').addClass 'active'
            return
        $('div.input-container input,div.input-container textarea').blur () ->
            $(this).closest('div.input-container').removeClass 'active'
            return
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
        mapStyles = [
            featureType: "poi"
            elementType: "labels"
            stylers: [visibility: "off"]
        ]
        mapOptions =
            zoom: 15
            center: map_center
            mapTypeControl: false
            scaleControl: false
            scrollWheel: false
            streetViewControl: false
            styles: mapStyles
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
            clearTimeout(@autoSaveTimer)
            $('div#event-modify-basics div.status').html 'Unsaved Changes'
            @autoSaveTimer = setTimeout (() =>
                @isEditing = false
                return
            ), 5000
            return
        # Auto-save timer
        setInterval (() =>
            @autoSave()
            return
        ), 10000
        # Time auto-complete
        originalStartTime = $('form.event-modify input[name=start_time]').val()
        originalEndTime = $('form.event-modify input[name=end_time]').val()
        $('form.event-modify input[name=start_time], form.event-modify input[name=end_time]').timeAutocomplete
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
        $('form.event-modify input[name=location]').keypress () =>
            keyword = $('form.event-modify input[name=location]').val()
            if keyword.trim() isnt ''
                googleAutocomplete.getQueryPredictions
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
                            matchContains: true
                            minLength: 0
                        $('form.event-modify input[name=location]').autocomplete("search","")
                        $('form.event-modify input[name=location]').on 'autocompleteselect', (event, ui) =>
                            @fetchCoordinates ui.item.id
                            return
                        return
            return
        return

Bazaarboy.event.modify.basics.init()