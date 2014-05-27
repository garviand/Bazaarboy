Bazaarboy.event.modify.tickets =
    ticketSubmitting: false
    newTicket: () ->
        $('div#edit-ticket div.step-2').hide()
        $('div#edit-ticket div.step-1').show()
        $('div#edit-ticket').removeAttr('data-id').removeClass('edit').addClass 'add'
        $('div#edit-ticket div.step-1').removeClass 'hide'
        $('div#edit-ticket div.step-1 span.type').html 'First, Choose a'
        $('div#edit-ticket div.step-2').addClass 'hide'
        $('div#edit-ticket div.step-2 span.type').html 'New'
        $('div#edit-ticket input').val ''
        $('div#edit-ticket textarea').val ''
        $('div#edit-ticket div.info a.blue-btn')
            .parent()
            .removeClass('columns')
            .addClass 'hide'
        $('div#edit-ticket div.info input.primary-btn').val('Add')
            .parent()
            .addClass('medium-centered').removeClass('end')
        @initDateTimeAutoComplete $('div#edit-ticket form')
        $('div#edit-ticket').fadeIn 300
        return
    editTicket: (ticket) ->
        Bazaarboy.get 'event/ticket/', {id:ticket}, (response) =>
          if response.status isnt 'OK'
              alert response.message
          else
              $('div#edit-ticket').removeClass('add').addClass 'edit'
              $('div#edit-ticket div.step-1').addClass 'hide'
              $('div#edit-ticket div.step-1 span.type').html 'Switch'
              $('div#edit-ticket div.step-2').removeClass 'hide'
              $('div#edit-ticket div.step-2 span.type').html 'Edit'
              $('div#edit-ticket input[name=name]').val response.ticket.name
              if response.ticket.price is 0
                  $('div#edit-ticket div.price input').val 0
                  $('div#edit-ticket div.price').addClass 'hide'
                  $('div#edit-ticket div.quantity').removeClass('medium-6').addClass('medium-12')
              else
                  $('div#edit-ticket input[name=price]').val response.ticket.price
                  $('div#edit-ticket div.price').removeClass 'hide'
                  $('div#edit-ticket div.quantity').removeClass('medium-12').addClass('medium-6')
              quantity = if response.ticket.quantity? then response.ticket.quantity else ''
              $('div#edit-ticket input[name=quantity]').val quantity
              $('div#edit-ticket textarea[name=description]').val response.ticket.description
              startTime = ''
              startDate = ''
              if response.ticket.start_time?
                  startTime = moment.utc response.ticket.start_time, 'YYYY-MM-DD HH:mm:ss'
                  startDate = startTime.local().format 'MM/DD/YYYY'
                  startTime = startTime.format 'h:mm A'
              $('div#edit-ticket textarea[name=start_date]').val startDate
              $('div#edit-ticket textarea[name=start_time]').val startTime
              endTime = ''
              endDate = ''
              if response.ticket.end_time?
                  endTime = moment.utc response.ticket.end_time, 'YYYY-MM-DD HH:mm:ss'
                  endDate = endTime.local().format 'MM/DD/YYYY'
                  endTime = endTime.format 'h:mm A'
              $('div#edit-ticket textarea[name=end_date]').val endDate
              $('div#edit-ticket textarea[name=end_time]').val endTime
              @initDateTimeAutoComplete $('div#edit-ticket')
              $('div#edit-ticket div.info a.blue-btn')
                  .parent()
                  .addClass('columns')
                  .removeClass 'hide'
              $('div#edit-ticket div.info input.primary-btn').val('Save')
                  .parent()
                  .removeClass('medium-centered').addClass('end')
              $('div#edit-ticket').attr('data-id', ticket).fadeIn 300
              $('body').animate {scrollTop: 0}, 300
          return
        return
    newPromo: () ->
      return
    initDateTimeAutoComplete: (form) ->
        # Time auto-complete
        originalStartTime = $(form).find('input[name=start_time]').val()
        originalEndTime = $(form).find('input[name=end_time]').val()
        $(form).find('input[name=start_time], input[name=end_time]').timeAutocomplete
            blur_empty_populate: false
            appendTo: '#menu-container'
        $(form).find('input[name=start_time]').val originalStartTime
        $(form).find('input[name=end_time]').val originalEndTime
        # Date auto-complete
        $(form).find('input[name=start_date]').pikaday
            format: 'MM/DD/YYYY'
            onSelect: () ->
                $(form).find('input[name=end_date]').pikaday 'gotoDate', this.getDate()
                $(form).find('input[name=end_date]').pikaday 'setMinDate', this.getDate()
                return
        $(form).find('input[name=end_date]').pikaday
            format: 'MM/DD/YYYY'
        return
    init: () ->
        scope = this
        $('a.new-ticket').click () =>
            @newTicket()
            return
        $('a.new-promo').click () =>
            return
        $('div.ticket-option div.top div.secondary-btn').click () ->
            ticket = $(this).closest('div.ticket-option').attr('data-id')
            scope.editTicket ticket
            return
        isEditTicketInAnimation = false
        $('div#edit-ticket div.cancel-btn').click () ->
            $('div#edit-ticket').fadeOut 300
            return
        $('div#edit-ticket div.type a.action-btn').click () ->
            if not isEditTicketInAnimation
                isFree = $(this).hasClass 'free'
                if isFree
                    $('div#edit-ticket div.price input').val 0
                    $('div#edit-ticket div.price').addClass 'hide'
                    $('div#edit-ticket div.quantity').removeClass('medium-6').addClass('medium-12')
                else
                    if parseInt($('div#edit-ticket div.price input').val()) is 0
                        $('div#edit-ticket div.price input').val ''
                    $('div#edit-ticket div.price').removeClass 'hide'
                    $('div#edit-ticket div.quantity').removeClass('medium-12').addClass('medium-6')
                isEditTicketInAnimation = true
                $('div#edit-ticket div.step-1').fadeOut 300, () ->
                    $('div#edit-ticket div.step-2').fadeIn 300, () ->
                        isEditTicketInAnimation = false
                        return
                    return
                return
        $('div#edit-ticket div.change-type').click () ->
            isEditTicketInAnimation = true
            $('div#edit-ticket div.step-2').fadeOut 300, () ->
                $('div#edit-ticket div.step-1').fadeIn 300, () ->
                    isEditTicketInAnimation = false
                    return
                return
            return
        $('div#edit-ticket a.blue-btn').click () ->
            ticketId = $('div#edit-ticket').attr 'data-id'
            if confirm 'Are you sure you want to delete this ticket?'
                Bazaarboy.post 'event/ticket/delete/', {id: ticketId}, (response) ->
                    if response.status isnt 'OK'
                        alert response.message
                    else
                        isEditTicketInAnimation = true
                        $('div#edit-ticket').fadeOut 300, () ->
                            $('div.ticket-option[data-id="' + ticketId + '"]').fadeOut 300, () ->
                                isEditTicketInAnimation = false
                                $(this).remove()
                                return
                            return
                    return
            return
        $('div#edit-ticket form').submit (event) ->
            event.preventDefault()
            if not scope.ticketSubmitting
                console.log scope.ticketSubmitting
                scope.ticketSubmitting = true
                isNew = $('div#edit-ticket').hasClass 'add'
                ticketId = $('div#edit-ticket').attr 'data-id'
                params = $(this).serializeObject()
                if isNew
                    params.event = eventId
                else
                    params.id = ticketId
                if params.quantity.trim().length is 0
                    if isNew
                        delete params.quantity
                    else
                        params.quantity = 'None'
                if params.start_date.trim().length != 0 and 
                   params.start_time.trim().length != 0
                    startDate = moment(params.start_date.trim(), 'MM/DD/YYYY')
                    if not startDate.isValid()
                        return
                    startTime = moment(params.start_time.trim(), 'h:mm A')
                    if not startTime.isValid()
                        return
                    params.start_time = moment(params.start_date.trim() + ' ' + params.start_time.trim(), 
                                               'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss')
                else
                    if isNew
                        delete params.start_time
                    else
                        params.start_time = 'None'
                if params.end_date.trim().length != 0 and
                   params.end_time.trim().length != 0
                    endDate = moment(params.end_date.trim(), 'MM/DD/YYYY')
                    if not endDate.isValid()
                        return
                    endTime = moment(params.end_time.trim(), 'h:mm A')
                    if not endTime.isValid()
                        return
                    params.end_time = moment(params.end_date.trim() + ' ' + params.end_time.trim(), 
                                             'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss')
                else
                    if isNew
                        delete params.end_time
                    else
                        params.end_time = 'None'
                endpoint = 'event/ticket/edit/'
                if isNew
                    endpoint = 'event/ticket/create/'
                Bazaarboy.post endpoint, params, (response) ->
                    if response.status is 'OK'
                        $('div#event-modify-tickets div.empty-state-container').addClass('hide')
                        $('div#event-modify-tickets div#action-canvas').removeClass('hide')
                        ticketOption = null
                        if isNew
                            ticketOption = $('div.templates div.ticket-option').clone()
                            $(ticketOption).attr 'data-id', response.ticket.pk
                            $(ticketOption).appendTo 'div#ticket-canvas'
                            $(ticketOption).find('div.top div.secondary-btn').click () ->
                                ticket = $(this).closest('div.ticket-option').attr('data-id')
                                scope.editTicket ticket
                                return
                        else
                            ticketOption = $('div.ticket-option[data-id="' + ticketId + '"]')
                        price = if response.ticket.price > 0 then '$' + response.ticket.price.toFixed(2) else 'Free'
                        $(ticketOption).find('div.price').html price
                        $(ticketOption).find('div.name').html response.ticket.name
                        $(ticketOption).find('div.description').html response.ticket.description
                        sold = if response.ticket.sold? then response.ticket.sold else 0
                        $(ticketOption).find('span.sold').html sold
                        quantity = if response.ticket.quantity then '/' + response.ticket.quantity else ''
                        $(ticketOption).find('span.quantity').html quantity
                        wording = 'RSVP\'d'
                        wordingObject = 'RSVPs'
                        if response.ticket.price > 0
                            wording = 'Sold'
                            wordingObject = 'Ticket Holders'
                        $(ticketOption).find('span.wording').html wording
                        $(ticketOption).find('span.wording-object').html wordingObject
                        $('div#edit-ticket').fadeOut 300, () ->
                            scope.ticketSubmitting = false
                            return
                    else
                        scope.ticketSubmitting = false
                        alert response.message
                    return
            return
        return

Bazaarboy.event.modify.tickets.init()