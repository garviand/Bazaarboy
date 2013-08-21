# Start namesapce
@Bazaarboy = 
    # Sub namespaces
    index: {}
    user: {}
    profile: {}
    event: {}
    admin: {}
    # Collapsed states, formats are like this:
    #       selector: [String] selector
    #       attr: [String] property to be animated
    #       expanded: [*] property value in expanded state
    #       collapsed: [*] property value in collapsed state
    collapseStates: []
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
    # Switch viewport states
    switchCollapsedStates: (cb) ->
        collapse = !$('body').hasClass('collapsed')
        _to = if collapse then 2 else 1
        collapseAnimations = []
        for element in @collapseStates
            animations = {}
            for attr in element[1]
                animations[attr[0]] = attr[_to]
            collapseAnimations.push($(element[0]).stop()
                                    .animate(animations, 300, 'easeInOutQuint')
                                    .promise())
        $.when.apply($, collapseAnimations).done () =>
            if collapse
                $('body').addClass('collapsed')
            else
                $('body').removeClass('collapsed')
            return cb?()
        return
    # Initialization
    init: () ->
        # Pass the timezone information back to server
        @post 'timezone/', {timezone: getTimezoneName()}
        # Sidebar
        @collapseStates = [
            ['div#wrapper_top div.logo', [['width', '186px', '60px']]]
            ['div#wrapper_top div.search', [['width', '750px', '876px']]]
            ['div#wrapper_sidebar', [['width', '186px', '60px']]]
            ['div#wrapper_content', [['width', '750px', '876px']]]
        ]
        $('div#wrapper_sidebar div.switch a').click () =>
            @switchCollapsedStates()
        return

Bazaarboy.init()