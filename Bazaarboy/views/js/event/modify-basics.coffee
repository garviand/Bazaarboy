Bazaarboy.event.modify.basics =
    save: (params, cb) ->=
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
    auto_save: () ->
        name = $("form.event-modify input[name=name]").val()
        summary = $("form.event-modify input[name=summary]").val()
        location = $("form.event-modify input[name=location]").val()
        latitude = $("form.event-modify input[name=latitude]").val()
        longitude = $("form.event-modify input[name=longitude]").val()
        startDate = $("form.event-modify input[name=start_date]").val()
        startTime = $("form.event-modify input[name=start_time]").val()
        if moment(startDate, 'MM/DD/YYYY').isValid() and moment(startTime, 'h:mm a').isValid()
            startTime = moment(startDate + ' ' + startTime, 'MM/DD/YYYY h:mm A')
        else
            startTime = ''
        endDate = $("form.event-modify input[name=end_date]").val()
        endTime = $("form.event-modify input[name=end_time]").val()
        if endDate.trim().length is 0 and endTime.trim().length is 0
            endTime = false
        else
            if not moment(endDate, 'MM/DD/YYYY').isValid()
                return
            if not moment(endTime, 'h:mm a').isValid()
                return
            endTime = moment(endDate + ' ' + endTime, 'MM/DD/YYYY h:mm A')
        Bazaarboy.event.modify.basics.save
            id: id
            start_time: startTime.utc().format('YYYY-MM-DD HH:mm:ss')
            end_time: if endTime then endTime.utc().format('YYYY-MM-DD HH:mm:ss') else 'none'
            name: name
            summary: summary
            location: location
            latitude: latitude
            longitude: longitude
        , (err, event) =>
            unless err
                console.log(event)
            else
                console.log(err)
            return
        return
    fetchCoordinates: (reference) ->
        location = $('form.event-modify input[name=location]').get(0)
        placesService = new google.maps.places.PlacesService(location)
        placesService.getDetails
            reference: reference
        , (result, status) ->
            if status is 'OK'
                $('form.event-modify input[name=latitude]')
                    .val result.geometry.location.lat()
                $('form.event-modify input[name=longitude]')
                    .val result.geometry.location.lng()
            return
        return
    init: () ->
        # AUTO-SAVE TIMER
        setInterval(@auto_save, 10000)
        # TIME AUTOCOMPLETE
        originalStartTime = $("form.event-modify input[name=start_time]").val()
        originalEndTime = $("form.event-modify input[name=end_time]").val()
        $("form.event-modify input[name=start_time], form.event-modify input[name=end_time]").timeAutocomplete
            blur_empty_populate: false
        $("form.event-modify input[name=start_time]").val(originalStartTime) 
        $("form.event-modify input[name=end_time]").val(originalEndTime)
        # DATE AUTOCOMPLETE
        $('form.event-modify input[name=start_date]').pikaday
            format: 'MM/DD/YYYY'
            onSelect: () ->
                $('form.event-modify input[name=end_date]').pikaday('gotoDate', this.getDate())
                $('form.event-modify input[name=end_date]').pikaday('setMinDate', this.getDate())
                return
        $('form.event-modify input[name=end_date]').pikaday
            format: 'MM/DD/YYYY'
        # Location Autocomplete
        googleAutocomplete = new google.maps.places.AutocompleteService()
        $('form.event-modify input[name=location]').keyup () =>
            keyword = $('form.event-modify input[name=location]').val()
            if keyword.trim() isnt ''
                googleAutocomplete.getQueryPredictions
                    types: ['establishment']
                    input: keyword
                , (predictions, status) =>
                    autocompleteSource = []
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
                    $('form.event-modify input[name=location]').on 'autocompleteselect'
                    , (event, ui) =>
                        @fetchCoordinates ui.item.id
                        return
                    return
            return
        return

Bazaarboy.event.modify.basics.init()