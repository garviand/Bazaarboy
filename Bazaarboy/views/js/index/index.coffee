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
                total_sales += purchase.amount
                rsvps.push [date.unix() * 1000, purchase.rsvps]
                sales.push [date.unix() * 1000, total_sales]
                return
            $(canvas).highcharts
                chart: {
                    type: 'area'
                },
                credits: {
                    enabled: false
                },
                colors: ["#4963E4", "#00BD84"],
                title: {
                    text: ''
                },
                legend: {
                    enabled: false
                },
                xAxis: 
                    gridLineWidth: 0
                    type: 'datetime'
                    dateTimeLabelFormats:
                        day: '%b %e'
                yAxis: [
                    labels:
                        format: '{value}'
                    title:
                        text: 'RSVPs'
                        style:
                            color: '#4963E4'
                    min: 0
                ,
                    labels:
                        format: '${value}'
                    title:
                        text: 'Total Sales'
                        style:
                            color: '#00BD84'
                    opposite: true
                    min: 0
                ]
                plotOptions:
                    area:
                        fillOpacity: .1
                        pointStart: 0
                        marker:
                            enabled: true
                            symbol: 'circle'
                            radius: 2
                            states:
                                hover:
                                    enabled: true
                series: [
                    name: 'RSVPs'
                    yAxis: 0
                    data: rsvps
                ,
                    name: 'Total Sales'
                    yAxis: 1
                    data: sales
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
                window.location = 'event/' + eventId
            else
                alert response.message
            return
    init: () ->
        scope = this
        # Create event
        $('div.create-event').click () ->
            profileId = $(this).attr('data-profile-id')
            scope.createEvent profileId
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
        $('div.current-event').each () ->
            scope.initGraph this
            return
        return

Bazaarboy.index.index.init()