@Bazaarboy.landing = 
    searchEvents: (value) ->
        Bazaarboy.get 'profile/search/', {keyword: value}, (response) ->
            if response.status is 'OK'
                profiles = response.profiles
                if profiles.length > 0
                    return profiles
                else
                    return []
            return
    init: () ->
        $('a.sign-up-submit').click () ->
            email = $('input[name=sign_up_email]').val()
            Bazaarboy.redirect 'register/?sem=' + email
            return
        $('a.see-how-btn').click () ->
            $('html, body').animate
                scrollTop: $("div.uses-container").offset().top
                , 500
            return
        $('body').on 'click', '.event_link', (event) ->
            eventUrl = $(this).data('url')
            document.location.href = eventUrl
            return
        $('input[name=event_name]').autocomplete
            html: true,
            source: (request, response) ->
                Bazaarboy.get 'event/search/', {keyword: request.term}, (results) ->
                    events = []
                    for evnt in results.events
                        thisLabel = '<div class="autocomplete_result event_link row" data-url="' + evnt.event_url + '" data-id="' + evnt.pk + '">'
                        if evnt.image_url?
                            thisLabel += '<div class="small-2 columns autocomplete_image" style="background-image:url(' + evnt.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;">&nbsp;</div>'
                            thisLabel += '<div class="small-10 columns autocomplete_name">' + evnt.name + '</div>'
                        else
                            thisLabel += '<div class="small-10 small-offset-2 columns autocomplete_name">' + evnt.name + '</div>'
                        thisLabel += '</div>'
                        events.push({label: thisLabel, value: evnt.name})
                    return response(events)
                return
        $('div.slider-container div.organizer-slider').slick(
            arrows: false
            autoplay: true
            autoplaySpeed: 5000
        )
        $('ul.slider-controls div.logo-container a').click () ->
            slideNum = $(this).closest('div.logo-container').data('slidenum')
            $('div.slider-container div.organizer-slider').slick('slickGoTo', slideNum)
            return
        $('div.slider-container div.organizer-slider').on 'beforeChange', (event, slick, currentSlide, nextSlide) ->
            $('ul.slider-controls div.logo-container').removeClass('active')
            $('ul.slider-controls div.logo-container[data-slidenum=' + nextSlide + ']').addClass('active')
            return
        return

Bazaarboy.landing.init()