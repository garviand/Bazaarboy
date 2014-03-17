Bazaarboy.event.index = 
    savingInProgress: false
    saveDescription: () ->
        description = $('div#event-description div.description div.inner').redactor('get')
        $('div.save-status').html 'Saving...'
        @savingInProgress = true
        Bazaarboy.post 'event/edit/', 
            id: eventId,
            description: description
        , (response) ->
            if response.status isnt 'OK'
                alert response.message
            else
                @savingInProgress = false
                setTimeout (() ->
                    $('div.save-status').html 'Saved'
                    return
                ), 500
            return
        return
    init: () ->
        latitude = parseFloat $('div.map-canvas').attr('data-latitude')
        longitude = parseFloat $('div.map-canvas').attr('data-longitude')
        if latitude isnt NaN and longitude isnt NaN
            $('div.map-canvas').removeClass 'hide'
            mapCenter = new google.maps.LatLng latitude, longitude
            mapOptions =
                zoom: 15
                center: mapCenter
                draggable: false
                mapTypeControl: false
                scaleControl: false
                panControl: false
                scrollwheel: false
                streetViewControl: false
                zoomControl: true
            map = new google.maps.Map document.getElementById('map-canvas'), mapOptions
            marker = new google.maps.Marker
                position: mapCenter
                map: map
                url: "https://maps.google.com/?saddr=#{latitude},#{longitude}"
            google.maps.event.addListener marker, 'click', () ->
                window.open @url, '_blank'
                return
        if design
            $('div#event-description div.description div.inner').redactor
                buttons: [
                    'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                    'alignment', '|',
                    'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                    'horizontalrule', 'table', 'image', 'video', 'link', '|',
                    'html'
                ]
                boldTag: 'b'
                italicTag: 'i'
                imageUpload: rootUrl + 'file/image/upload/'
            $('a.save.primary-btn').click () =>
                @saveDescription()
                return
        return

Bazaarboy.event.index.init()