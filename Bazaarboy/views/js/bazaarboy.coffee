# Start namesapce
@Bazaarboy = 
    # Sub namespaces
    index: {}
    user: {}
    profile: {}
    event: {
        modify: {}
    }
    list: {}
    reward: {}
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
    # Other useful functions
    trim: (params, required=null) ->
        opts = {}
        output = {}
        for key,value of params
            if not required? or required.indexOf(key) > 1
                value = value.trim()
            output[key] = value
        return output
    stripEmpty: (params, keys) ->
        output = {}
        for key,value of params
            if keys.indexOf(key) == -1 or value.trim().length isnt 0
                output[key] = value.trim()
        return output
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
    # Initialization
    init: () ->
        scope = this
        # Pass the timezone information back to server
        @post 'timezone/', {timezone: getTimezoneName()}
        # Initialize Foundation
        $(document).foundation()
        # Adjust footer position when window resizes
        ###
        $(document).ready () =>
            @adjustBottomPosition()
            return
        $(window).resize () =>
            @adjustBottomPosition()
            return
        ###
        return

Bazaarboy.init()