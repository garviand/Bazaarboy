Bazaarboy.profile.index = 
    init: () ->
        latitude = parseFloat $('div.map-canvas').attr('data-latitude')
        longitude = parseFloat $('div.map-canvas').attr('data-longitude')
        if not isNaN(latitude) and not isNaN(longitude)
            # GET ADDRESS
            geocoder = new google.maps.Geocoder()
            latlng = new google.maps.LatLng(latitude, longitude)
            geocoder.geocode {'latLng': latlng}, (results, status) ->
                if results[0]
                    loc = results[0]['formatted_address'].split(",")
                    street = loc[0]
                    city_zip = loc[1] + ", " + loc[2]
                    $("div#event-location div.address span.street-address").html(street)
                    $("div#event-location div.address span.city-zip").html(city_zip)
                    $("div#event-location div.address").removeClass("hide")
                return 
            $('div.map-canvas').removeClass 'hide'
            mapCenter = new google.maps.LatLng latitude, longitude
            mapStyles = [
                {
                    featureType: "administrative"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "on"
                        }
                        {
                            saturation: -100
                        }
                        {
                            lightness: 20
                        }
                    ]
                }
                {
                    featureType: "road"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "on"
                        }
                        {
                            saturation: -100
                        }
                        {
                            lightness: 40
                        }
                    ]
                }
                {
                    featureType: "water"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "on"
                        }
                        {
                            saturation: -10
                        }
                        {
                            lightness: 30
                        }
                    ]
                }
                {
                    featureType: "landscape.man_made"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "simplified"
                        }
                        {
                            saturation: -60
                        }
                        {
                            lightness: 10
                        }
                    ]
                }
                {
                    featureType: "landscape.natural"
                    elementType: "all"
                    stylers: [
                        {
                            visibility: "simplified"
                        }
                        {
                            saturation: -60
                        }
                        {
                            lightness: 60
                        }
                    ]
                }
            ]
            mapOptions =
                zoom: 15
                center: mapCenter
                draggable: false
                mapTypeControl: false
                scaleControl: false
                panControl: false
                scrollwheel: false
                streetViewControl: false
                zoomControl: false
                styles: mapStyles
            map = new google.maps.Map document.getElementById('map-canvas'), mapOptions
            iconImage =
                url: staticUrl + "images/map_icon.png"
                size: new google.maps.Size(200, 111)
                origin: new google.maps.Point(0, 15)
                anchor: new google.maps.Point(100, 55)
            marker = new google.maps.Marker
                position: mapCenter
                map: map
                url: "https://maps.google.com/?saddr=#{latitude},#{longitude}"
            google.maps.event.addListener marker, 'click', () ->
                window.open @url, '_blank'
                return
        return

Bazaarboy.profile.index.init()