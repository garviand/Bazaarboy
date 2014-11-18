Bazaarboy.event.format_full_screen =
    ticketMenu: undefined
    ticketId: undefined
    DropDown: (el) ->
        this.dd = el
        this.placeholder = this.dd.children('span')
        this.opts = this.dd.find('ul.dropdown > li')
        this.val = ''
        this.index = -1
        this.ticket = undefined
        this.initEvents()
    init: () ->
        scope = this
        if $('.tix-type').length == 1
            scope.ticketId = $('.tix-type').data('id')
        @DropDown:: =
            initEvents: ->
                obj = this
                obj.dd.on "click", (event) ->
                    $(this).toggleClass "active"
                    false
                    return
                obj.opts.on "click", ->
                    opt = $(this)
                    obj.val = opt.text()
                    obj.index = opt.index()
                    obj.placeholder.text obj.val
                    scope.ticketId = opt.find('a').data('id')
                    return
                return
            getValue: ->
                @val
                return
            getIndex: ->
                @index
                return
        @ticketMenu = new @DropDown($('#dd'))
        $(document).click () ->
            #$('.ticket-dropdown').removeClass('active')
            return
        $("form.hero-ticket-form button[type=submit], .tix-type").click (e) ->
            e.preventDefault()
            ticketId = scope.ticketId
            if not $("div#tickets div.ticket[data-id=" + ticketId + "]").hasClass('active')
                $("div#tickets div.ticket[data-id=" + ticketId + "] div.ticket-top").click()
            if not Bazaarboy.event.index.overlayAnimationInProgress
                $("html, body").animate({ scrollTop: 0 }, "fast")
                if $('div#wrapper-overlay').hasClass('hide')
                    Bazaarboy.event.index.overlayAnimationInProgress = true
                    $('div#wrapper-overlay').css('opacity', 0).removeClass('hide')
                    $('div#tickets').css('opacity', 0).removeClass('hide')
                    $('div#wrapper-overlay').animate {opacity: 1}, 300
                    $('div#tickets').animate {opacity: 1}, 300, () =>
                        Bazaarboy.event.index.overlayAnimationInProgress = false
                        return
        return

Bazaarboy.event.format_full_screen.init()