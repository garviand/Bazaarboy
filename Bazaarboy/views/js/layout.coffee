# Start namesapce
@Bazaarboy = 
    # Sub namespaces
    index: {}
    user: {}
    profile: {}
    event: {}
    admin: {}
    # Shortcut for endpoint redirect
    redirect: (endpoint) ->
        redirectUrl = rootUrl
        # Special keyword for index for code readablity
        if endpoint isnt 'index'
            redirectUrl = rootUrl + endpoint
        window.location.href = redirectUrl
        return
    # Shortcut for $.get, which appends root url and parses response into JSON
    get: (endpoint, params={}, cb) ->
        params.csrfmiddlewaretoken = csrfToken
        promise = $.get rootUrl + endpoint, params, (data) ->
            response = $.parseJSON data
            return cb? response
        return promise
    # Shortcut for $.post, similar to the shortcut for $.get
    post: (endpoint, params={}, cb) ->
        params.csrfmiddlewaretoken = csrfToken
        promise = $.post rootUrl + endpoint, params, (data) ->
            response = $.parseJSON data
            return cb? response
        return promise
    # Layout functions
    adjustBottomPosition: () ->
        windowHeight = $(window).height()
        topHeight = $('div#wrapper_top').outerHeight()
        if $('div#wrapper_top').hasClass('hidden')
            topHeight = 0
        contentHeight = $('div#wrapper_content').outerHeight()
        bottomHeight = $('div#wrapper_bottom').outerHeight()
        if windowHeight - bottomHeight > topHeight + contentHeight
            $('div#wrapper_bottom').css
                'position': 'fixed'
                'bottom': 0
        else
            $('div#wrapper_bottom').css
                'position': ''
                'bottom': ''
        return
    # Create Empty Event
    createEvent: (profileId) ->
        Bazaarboy.post 'event/create/', {profile: profileId}, (response) =>
            if response.status is 'OK'
                Bazaarboy.redirect 'event/' + response.event.pk + '/'
            else
                alert response.message
            return
        return
    # Initialization
    init: () ->
        scope = this
        # Pass the timezone information back to server
        @post 'timezone/', {timezone: getTimezoneName()}
        # Adjust footer position when window resizes
        $(document).ready () =>
            @adjustBottomPosition()
            return
        $(window).resize () =>
            @adjustBottomPosition()
            return
        $('#wrapper_top .controls .user_create_event a').click (e) ->
            e.preventDefault()
            profileId = $(this).data('id')
            scope.createEvent profileId
            return
        return

Bazaarboy.init()