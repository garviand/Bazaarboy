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
        launchedTime = $(eventFrame).attr('data-launched-time')
        launchedTime = moment launchedTime, 'YYYY-MM-DD HH:mm:ss'
        now = moment()
        canvas = $(eventFrame).find('div.graph-canvas')
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
                data: [
                    [launchedTime.unix() * 1000, 0]
                    [now.unix() * 1000, 0]
                ]
            ,
                name: 'Total Sale'
                type: 'spline'
                yAxis: 1
                data: [
                    [launchedTime.unix() * 1000, 0]
                    [now.unix() * 1000, 0]
                ]
            ]
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