# Start namesapce
@Bazaarboy = 
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
            return cb response
        return
    # Shortcut for $.post, similar to the shortcut for $.get
    post: (endpoint, params={}, cb) ->
        params.csrfmiddlewaretoken = csrfToken
        $.post rootUrl + endpoint, params, (data) ->
            response = $.parseJSON data
            return cb response
        return
    # Sub namespaces
    index: {}
    user: {}
    event: {}
    admin: {}
    # Collapsed states, formats are like this:
    #       selector: [String] selector
    #       attr: [String] property to be animated
    #       expanded: [*] property value in expanded state
    #       collapsed: [*] property value in collapsed state
    collapsedStates: {}
    # Initialization
    init: () ->
        # Sidebar
        @collapsedStates = [
            selector: 'div#wrapper_top div.logo'
            attr: 'width'
            expanded: '186px'
            collapsed: '60px'
        ]
        $('div#wrapper_sidebar div.switch a').click () =>
            collapse = !$('body').hasClass('collapsed')
            _to = if collapse then 'collapsed' else 'expanded'
            for selector, value of @collapsedStates
                animation = {}
                animation[value.attr] = value[_to]
                $(value.selector).animate animation, 200, () =>
                    if collapse
                        $('body').addClass('collapsed')
                    else
                        $('body').removeClass('collapsed')
                    return
            return
        return

Bazaarboy.init()