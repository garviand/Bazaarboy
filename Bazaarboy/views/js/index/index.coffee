Bazaarboy.index.index = 
    createEvent: (profileId) ->
        Bazaarboy.post 'event/create/', {profile: profileId}, (response) =>
            if response.status is 'OK'
                Bazaarboy.redirect 'event/' + response.event.pk + '/basics/'
            else
                alert response.message
            return
        return
    initGraph: (eventFrame) ->
        eventId = $(eventFrame).data('id')
        launchedTime = $(eventFrame).attr('data-launched-time')
        launchedTime = moment launchedTime, 'YYYY-MM-DD HH:mm:ss'
        now = moment()
        canvas = $(eventFrame).find('div.graph-canvas')
        rsvps = []
        sales = []
        total_sales = 0
        Bazaarboy.get 'event/data/', {id: eventId}, (response) =>
            if Object.keys(response.purchases).length == 0
                rsvps.push [launchedTime.unix() * 1000, 0]
                sales.push [launchedTime.unix() * 1000, 0]
            $.each response.purchases, (index, purchase) ->
                date = moment purchase.date, 'YYYY-MM-DD HH:mm:ss'
                rsvps.push [date.unix() * 1000, purchase.rsvps]
                sales.push [date.unix() * 1000, purchase.amount]
                return
            rsvps = rsvps.sort()
            sales = sales.sort()
            for sale in sales
                total_sales += sale[1]
                sale[1] = total_sales
            $(canvas).highcharts
                chart:
                    type: 'area'
                    marginTop: 30
                    marginRight: 20
                    style:
                        fontFamily: 'helvetica'
                credits:
                    enabled: false
                colors: ["#C57724", "#00BD84"]
                title:
                    text: ''
                legend:
                    enabled: false
                tooltip:
                    formatter: () ->
                        return Highcharts.dateFormat('%b %e', new Date(this.x)) + '<br /><b>' + this.y + ' RSVPs</b>'
                    backgroundColor: '#C57724'
                    borderWidth: 0
                    dateTimeLabelFormats:
                        millisecond: '%b %e'
                        second: '%b %e'
                        minute: '%b %e'
                        hour: '%b %e'
                        day: '%b %e'
                        week: '%b %e'
                    style:
                        color: '#FFF'
                    shadow: false
                xAxis: 
                    allowDecimals: false
                    lineColor: '#D6D6D6'
                    gridLineColor: '#F6F6F6'
                    gridLineWidth: 1
                    tickLength: 0
                    type: 'datetime'
                    dateTimeLabelFormats:
                        millisecond: '%b %e'
                        second: '%b %e'
                        minute: '%b %e'
                        hour: '%b %e'
                        day: '%b %e'
                    labels:
                        style:
                            color: '#D6D6D6'
                            fontWeight: 'bold'
                yAxis:
                    lineWidth: 1
                    lineColor: '#D6D6D6'
                    offset: -3
                    gridLineWidth: 0
                    labels:
                        format: '{value}'
                    title:
                        text: ''
                        style:
                            color: '#4963E4'
                    min: 0
                    labels:
                        style:
                            color: '#D6D6D6'
                            fontWeight: 'bold'
                plotOptions:
                    area:
                        fillOpacity: .25
                        pointStart: 0
                        marker:
                            enabled: false
                            symbol: 'circle'
                            radius: 2
                            states:
                                hover:
                                    enabled: true
                series: [
                    name: 'RSVPs'
                    yAxis: 0
                    data: rsvps
                ]
            return
        return
    loadGraph: (eventFrame) ->
        return
    deleteEvent: (eventId) ->
        Bazaarboy.post 'event/delete/', {id: eventId}, (response) =>
            if response.status is 'OK'
                return 'OK'
            else
                alert response.message
            return
        return
    launchEvent: (eventId) ->
        Bazaarboy.post 'event/launch/', {id: eventId}, (response) =>
            if response.status is 'OK'
                window.location = '/event/' + eventId + '#launch'
            else
                alert response.message
            return
    init: () ->
        scope = this
        # Rewards
        $('div.active-rewards a.show-btn').click () ->
            $('div.active-rewards div.reward-list').slideDown(200)
        # Collaboration Request
        $('div.request a.accept-request').click () ->
            requestId = $(this).data('id')
            thisRequest = $(this).closest('div.request')
            Bazaarboy.post 'event/organizer/request/accept/', {id:requestId}, (response) ->
                if response.status is 'OK'
                    thisRequest.html('<div class="small-12 text columns">Request Accepted! Refreshing...</div>')
                    setTimeout -> 
                        location.reload()
                    , 1000
                else
                    swal response.message
                return
            return
        $('div.request a.reject-request').click () ->
            requestId = $(this).data('id')
            thisRequest = $(this).closest('div.request')
            swal
                title: "Are You Sure?"
                text: "Are you sure you want to reject this collaboration request?"
                type: "warning"
                showCancelButton: true
                confirmButtonText: "Yes"
                closeOnConfirm: true
                , ->
                    Bazaarboy.post 'event/organizer/request/reject/', {id:requestId}, (response) ->
                        if response.status is 'OK'
                            thisRequest.html('<div class="small-12 text columns">Request Rejected...</div>')
                        else
                            swal response.message
                        return
            return
        # Create event
        $('div.create-event').click () ->
            profileId = $(this).attr('data-profile-id')
            scope.createEvent profileId
            return
        $('a.events-filter').click () ->
            $('div#wrapper-sidebar a.sidebar-item.events-filter').removeClass('selected')
            filter = $(this)
            $('#wrapper-dashboard div.event-tiles-container.active').fadeOut 300, () ->
                $('#wrapper-dashboard div.graph-canvas').empty()
                $('#wrapper-dashboard div.event-tiles-container.active').removeClass('active')
                if filter.hasClass('events-filter-summary')
                    $('div#wrapper-sidebar a.sidebar-item.events-filter-summary').addClass('selected')
                    $('div.header-title div.text span.sub').text 'Events Overview'
                    $('#wrapper-dashboard div.summary-events').addClass('active')
                    $('#wrapper-dashboard div.summary-events').fadeIn 300, () ->
                        $('div.current-event, div.past-event, div.past-event-attention').each () ->
                            scope.initGraph this
                            return
                        return
                if filter.hasClass('events-filter-current')
                    $('div#wrapper-sidebar a.sidebar-item.events-filter-current').addClass('selected')
                    $('div.header-title div.text span.sub').text 'Current Events'
                    $('#wrapper-dashboard div.current-events').addClass('active')
                    $('#wrapper-dashboard div.current-events').fadeIn 300, () ->
                        $('div.current-event').each () ->
                            scope.initGraph this
                            return
                        return
                if filter.hasClass('events-filter-draft')
                    $('div#wrapper-sidebar a.sidebar-item.events-filter-draft').addClass('selected')
                    $('div.header-title div.text span.sub').text 'Draft Events'
                    $('#wrapper-dashboard div.draft-events').addClass('active')
                    $('#wrapper-dashboard div.draft-events').fadeIn 300
                if filter.hasClass('events-filter-past')
                    $('div#wrapper-sidebar a.sidebar-item.events-filter-past').addClass('selected')
                    $('div.header-title div.text span.sub').text 'Past Events'
                    $('#wrapper-dashboard div.past-events').addClass('active')
                    $('#wrapper-dashboard div.past-events').fadeIn 300, () ->
                        $('div.past-event').each () ->
                            scope.initGraph this
                            return
                        return
                return
            return
        $('a.add-to-list-btn').click (e) ->
            $('div#add-list-modal span.event-name').html $(this).data('name')
            $('div#add-list-modal span.attendee-count').html $(this).data('count')
            $('div#add-list-modal input[name=event_id]').val $(this).data('id')
            $('div#add-list-modal').foundation('reveal', 'open')
            return
        $(document).on 'close.fndtn.reveal', 'div#add-list-modal', () ->
            $('div#add-list-modal input[name=event_id]').val ''
            $('div#add-list-modal div.list').removeClass 'active'
            return
        $('div#add-list-modal a.add-cancel-btn').click (e) ->
            $('div#add-list-modal').foundation('reveal', 'close')
            return
        $('body').on 'click', 'div#add-list-modal div.list', (e) ->
            $(this).toggleClass 'active'
            return
        $('div#add-list-modal a.create-list').click () ->
            $('div#add-list-modal div.status').html 'Creating...'
            $('div#add-list-modal div.submit-actions a').css('display','none')
            profileId = $('div#add-list-modal input[name=profile_id]').val()
            eventId = $('div#add-list-modal input[name=event_id]').val()
            list_name = $('div#add-list-modal input[name=list_name]').val()
            if list_name.trim() isnt ''
                Bazaarboy.post 'lists/create/', {profile:profileId, name:list_name, is_hidden:1}, (response) ->
                    if response.status is 'OK'
                        listId = response.list.pk
                        $('div#add-list-modal div.status').html 'Successfully Created List! Adding Members...'
                        Bazaarboy.post 'lists/add/event/', {id:listId, event:eventId}, (response) ->
                            if response.status is 'OK'
                                newList = $('div.list-template').clone()
                                newList.attr('data-id', response.list.pk)
                                newList.find('div.list-name').html(response.list.name)
                                newList.find('div.list-action').html(response.added + ' Members')
                                newList.removeClass('hide')
                                $('div#add-list-modal div.lists').prepend(newList)
                                $('div#add-list-modal div.status').html 'Congrats! List was Created and ' + response.added + ' Attendees were added.'
                            else
                                swal 'List Was Created, But there was an error: ' + response.message
                            $('div#add-list-modal div.submit-actions a').css('display','block')
                            return
                    else
                        swal 'Could not create list'
                        $('div#add-list-modal div.submit-actions a').css('display','block')
                    $('div#add-list-modal input[name=list_name]').val('')
                    return
            else
                swal 'List name can\'t be empty'
                $('div#add-list-modal div.submit-actions a').css('display','block')
            return
        $('div#add-list-modal a.submit-add-btn').click () ->
            $('div#add-list-modal div.status').html 'Adding Attendees to Lists...'
            $('div#add-list-modal div.submit-actions a').css('display','none')
            eventId = $('div#add-list-modal input[name=event_id]').val()
            selected_lists = $('div#add-list-modal div.lists div.list.active')
            num_lists = selected_lists.length
            error_lists = 0
            num_finished = 0
            if num_lists > 0
                $.each selected_lists, (list) ->
                    Bazaarboy.post 'lists/add/event/', {id:$(this).data('id'), event:eventId}, (response) ->
                        if response.status is 'OK'
                            $('div#add-list-modal div.status').html(num_finished + 'Lists Complete - ' + (num_lists - num_finished) + 'Lists Remaining')
                        else
                            error_lists++
                        num_finished++
                        if (num_lists - num_finished) is 0
                            if error_lists > 0
                                swal 'Lists added, but some attendees may have been left out'
                            else
                                swal
                                    title: "Success"
                                    text: "The Attendees have been Added!"
                                    type: "success"
                                    , ->
                                        $('div#add-list-modal').foundation('reveal', 'close')
                                        return
                            $('div#add-list-modal div.status').html '&nbsp;'
                            $('div#add-list-modal div.submit-actions a').css('display','block')
                        return
                    return
            else
                swal 'You Must Select at least One List!'
            return
        $('div.draft-event a.delete-draft').click (e) ->
            e.preventDefault()
            deleteConfirm = confirm("All information (including RSVPs) from this event will be lost. Are you sure you want to delete?")
            eventId = $(this).data('id')
            if deleteConfirm
                eventId = $(this).data('id')
                scope.deleteEvent(eventId)
                $(this).parents('div.draft-event').fadeOut()
            return
        $('div.draft-event a.launch-draft').click (e) ->
            eventId = $(this).data('id')
            scope.launchEvent(eventId)
            $(this).html("Launching...")
            return
        # Initialize graphs
        $('div.current-event, div.past-event').each () ->
            scope.initGraph this
            return
        return

Bazaarboy.index.index.init()