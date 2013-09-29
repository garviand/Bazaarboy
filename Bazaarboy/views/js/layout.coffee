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
        $.get rootUrl + endpoint, params, (data) ->
            response = $.parseJSON data
            return cb? response
        return
    # Shortcut for $.post, similar to the shortcut for $.get
    post: (endpoint, params={}, cb) ->
        params.csrfmiddlewaretoken = csrfToken
        $.post rootUrl + endpoint, params, (data) ->
            response = $.parseJSON data
            return cb? response
        return
    # Layout functions
    adjustBottomPosition: () ->
        windowHeight = $(window).height()
        topHeight = $('div#wrapper_top').outerHeight()
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
    # Initialization
    init: () ->
        # Pass the timezone information back to server
        @post 'timezone/', {timezone: getTimezoneName()}
        # Adjust footer position when window resizes
        @adjustBottomPosition()
        $(window).resize () =>
            @adjustBottomPosition()
            return
        return

Bazaarboy.init()