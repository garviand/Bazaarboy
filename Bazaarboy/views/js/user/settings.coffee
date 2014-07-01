Bazaarboy.user.settings =
    isEditing: false
    map: undefined
    marker: undefined
    image: undefined
    uploads:
        image: undefined
    createEvent: (profileId) ->
        Bazaarboy.post 'event/create/', {profile: profileId}, (response) =>
            if response.status is 'OK'
                Bazaarboy.redirect 'event/' + response.event.pk + '/basics/'
            else
                alert response.message
            return
        return
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
        $('div#user-settings div.status').html 'Saving...'
        console.log save_data
        @save
            id: profileId
            name: save_data.name
            email: save_data.email
            description: save_data.description
            location: save_data.location
            latitude: save_data.latitude
            longitude: save_data.longitude
            phone: save_data.phone
            link_website: save_data.link_website
            link_facebook: save_data.link_facebook
        , (err, event) =>
            unless err
                setTimeout (() ->
                    $('div#user-settings div.status').html 'Saved'
                    return
                ), 1000
            else
                $('div#user-settings div.status').html err.message
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
    startEditingLogoImage: () ->
        scope = this
        $('<img>')
            .attr('src', mediaUrl + @uploads.image.source)
            .load () ->
                $('div#user-settings div.logo div.logo_image')
                    .html('')
                $('div#user-settings div.logo div.logo_image')
                    .append(this)
                $('div#user-settings div.logo a.upload')
                    .addClass('hide')
                $('div#user-settings div.logo a.delete')
                    .addClass('hide')
                $('div#user-settings div.logo a.save')
                    .removeClass('hide')
                $('div#user-settings div.logo a.cancel')
                    .removeClass('hide')
                return
        return
    stopEditingLogoImage: () ->
        $('div#user-settings div.logo a.upload')
            .removeClass('hide')
        $('div#user-settings div.logo a.delete')
            .removeClass('hide')
        $('div#user-settings div.logo a.save')
            .addClass('hide')
        $('div#user-settings div.logo a.cancel')
            .addClass('hide')
        return
    saveLogoImage: () ->
        @save {image: @uploads.image.pk, id: profileId}, (err, profile) =>
            unless err
                @uploads.image = null
                @stopEditingLogoImage()
            else
                alert err.message
            return
        return
    deleteLogoImage: () ->
        if confirm('Are you sure you want to delete the logo?')
            @save {image: 'delete', id: profileId}, (err, profile) =>
                unless err
                    @image = null
                    $('div#user-settings div.logo div.logo_image').html('')
                else
                    alert err.message
                return
        return
    init: () ->
        scope = this
        $('div.create-event').click () ->
            profileId = $(this).attr('data-profile-id')
            scope.createEvent profileId
            return
        $('div#user-settings div.logo a.upload').click () ->
            $('div#user-settings form.upload_logo input[name=image_file]').click()
            return
        $('div#user-settings div.logo a.delete').click () =>
            @deleteLogoImage()
            return
        $('div#user-settings div.logo a.save').click () =>
            @saveLogoImage()
            return
        $('div#user-settings div.logo div.logo a.cancel').click () ->
            return
        $('div#user-settings form.upload_logo input[name=image_file]').fileupload
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
            $('div#user-settings div.status').html 'Editing'
            return
        # Is User Editing Info
        $('form.profile-settings').find('input, textarea').keyup () =>
            @isEditing = true
            $('div#user-settings div.status').html 'Editing'
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
        $('form.profile-settings input[name=location]').keypress (e) =>
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
                            matchContains: true
                            minChars: 0
                        $('form.profile-settings input[name=location]').autocomplete("search"," ")
                        $('form.profile-settings input[name=location]').on 'autocompleteselect', (event, ui) =>
                            @fetchCoordinates ui.item.id
                            return
                        return
            return
        return

Bazaarboy.user.settings.init()