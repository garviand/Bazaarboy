Bazaarboy.event.modify.basics = 
    init: () ->
        # INIT TIME AUTOCOMPLETE
        originalStartTime = $("form.event-modify input[name=start_time]").val()
        originalEndTime = $("form.event-modify input[name=end_time]").val()
        $("form.event-modify input[name=start_time], form.event-modify input[name=end_time]").timeAutocomplete
            blur_empty_populate: false
        $("form.event-modify input[name=start_time]").val(originalStartTime) 
        $("form.event-modify input[name=end_time]").val(originalEndTime)
        # INIT DATE AUTOCOMPLETE
        $('form.event-modify input[name=start_date]').pikaday
            format: 'MM/DD/YYYY'
            onSelect: () ->
                $('form.event-modify input[name=end_date]').pikaday('gotoDate', this.getDate())
                $('form.event-modify input[name=end_date]').pikaday('setMinDate', this.getDate())
                return
        $('form.event-modify input[name=end_date]').pikaday
            format: 'MM/DD/YYYY'
        return

Bazaarboy.event.modify.basics.init()