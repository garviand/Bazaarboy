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
        rsvps = [[launchedTime.unix() * 1000, 0]]
        sales = [[launchedTime.unix() * 1000, 0]]
        total_sales = 0
        Bazaarboy.get 'event/data/', {id: eventId}, (response) =>
            for purchase in response.purchases
                date = moment purchase.date, 'YYYY-MM-DD HH:mm:ss'
                total_sales += purchase.amount
                rsvps.push [date.unix() * 1000, purchase.rsvps]
                sales.push [date.unix() * 1000, total_sales]
            $(canvas).highcharts
                title:
                    text: null
                credits:
                    enabled: false
                xAxis: 
                    type: 'datetime'
                    dateTimeLabelFormats:
                        day: '%b %e'
                yAxis: [
                    labels:
                        format: '{value}'
                    title:
                        text: 'RSVPs'
                    min: 0
                ,
                    labels:
                        format: '${value}'
                    title:
                        text: 'Total Sale'
                    opposite: true
                    min: 0
                ]
                series: [
                    name: 'RSVPs'
                    type: 'spline'
                    yAxis: 0
                    data: rsvps
                ,
                    name: 'Total Sale'
                    type: 'spline'
                    yAxis: 1
                    data: sales
                ]
            return
        return
    loadGraph: (eventFrame) ->
        return
    init: () ->
        scope = this
        # Create event
        $('div.create-event').click () ->
            profileId = $(this).attr('data-profile-id')
            scope.createEvent profileId
            return
        # Initialize graphs
        $('div.current-event').each () ->
            scope.initGraph this
            return
        return

Bazaarboy.index.index.init()