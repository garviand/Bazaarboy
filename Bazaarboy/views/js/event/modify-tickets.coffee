Bazaarboy.event.modify.tickets =
    ticketSubmitting: false
    reordering: false
    newTicket: () ->
        $('div.custom-field-container:not(.template)').remove()
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
              $('div.custom-field-container:not(.template)').remove()
              if response.ticket.extra_fields.length > 0
                  extraFields = response.ticket.extra_fields.replace(new RegExp("u'", "g"),"'")
                  extraFields = extraFields.replace(new RegExp("\'", "g"),"\"")
                  extraFields = JSON.parse extraFields
                  for field_name, field_options of extraFields
                      newField = $('div.custom-fields-container div.custom-field-container.template').clone()
                      newField.find('input.field_name').val field_name
                      newField.find('input.field_options').val field_options
                      newField.removeClass 'hide'
                      newField.removeClass 'template'
                      $('div.custom-fields-container').prepend(newField)
              $('div#edit-ticket').removeClass('add').addClass 'edit'
              $('div#edit-ticket div.step-1').addClass 'hide'
              $('div#edit-ticket div.step-1 span.type').html 'Switch'
              $('div#edit-ticket div.step-2').removeClass 'hide'
              $('div#edit-ticket div.step-2 span.type').html 'Edit'
              $('div#edit-ticket input[name=name]').val response.ticket.name
              if response.ticket.request_address
                  $('div#edit-ticket input[name=request_address]').prop('checked', true)
              else
                  $('div#edit-ticket input[name=request_address]').prop('checked', false)
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
    savePromo: (newPromo) ->
        if not @promoSubmitting
            params = $('form#promo-form').serializeObject()
            params.start_time = params.promo_start_time
            params.event = eventId
            if params.start_time isnt undefined and params.start_time.trim().length != 0
                params.start_time = moment(params.start_time.trim(), 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss')
                if not params.start_time
                    alert 'Invalid Start Date'
            else if params.start_time.trim().length == 0
                params.start_time = 'none'
            if params.expiration_time isnt undefined and params.expiration_time.trim().length != 0
                params.expiration_time = moment(params.expiration_time.trim(), 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss')
                if not params.expiration_time
                    alert 'Invalid Expiration Date'
            else if params.expiration_time.trim().length == 0
                params.expiration_time = 'none'
            if isNaN(parseInt(params.discount))
                alert 'Discount Amount Must Be A Number'
                return
            if $('div#promos form#promo-form a.promo-type.active').attr('data-type') is 'number'
                params.amount = parseInt(params.discount)
                params.discount = ''
            else
                params.discount = parseFloat(params.discount) / 100
                if params.discount > 1
                    alert 'Percentage Must Be Between 1 and 100'
                    return
            selectedTickets = $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket.selected').length
            linkedTickets = 0
            failedLinks = 0
            if selectedTickets > 0
                if newPromo
                    Bazaarboy.post 'event/promo/create/', params, (response) ->
                        if response.status is 'OK'
                            promo_id = response.promo.pk
                            promo_code = response.promo.code
                            $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket.selected').each () ->
                                ticket_id = parseInt($(this).attr('data-id'))
                                Bazaarboy.post 'event/promo/link/', {id:promo_id, ticket:ticket_id}, (response) ->
                                    if response.status isnt 'OK'
                                        alert response.message
                                    linkedTickets++
                                    if linkedTickets == selectedTickets
                                        newPromo = $('div.promo-template').clone()
                                        newPromo.find('div.promo-name').html promo_code
                                        newPromo.attr('data-id', promo_id)
                                        newPromo.find('a.edit-promo').attr('data-id', promo_id)
                                        $('div.promo-template').after newPromo
                                        newPromo.removeClass 'promo-template'
                                        newPromo.removeClass 'hide'
                                        $('div#promos div.edit').fadeOut 300, () ->
                                            $('div#promos form#promo-form a.promo-type').removeClass 'active'
                                            $('div#promos form#promo-form a.promo-type').eq(0).addClass 'active'
                                            $('div#promos form#promo-form input').val ''
                                            $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass 'selected'
                                            $('div#promos div.content').fadeIn 300
                                        return
                                    return
                                return
                        else
                            alert response.message
                        return
                else
                    $("div.promo").each () ->
                        if parseInt($(this).attr('data-id')) is parseInt($('form#promo-form').attr('data-id'))
                            $(this).remove()
                        return
                    params.id = $('form#promo-form').attr('data-id')
                    params.id = parseInt(params.id)
                    console.log params
                    Bazaarboy.post 'event/promo/edit/', params, (response) ->
                        if response.status is 'OK'
                            amount_claimed = response.claimed
                            promo_id = response.promo.pk
                            promo_code = response.promo.code
                            $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket:not(.selected)').each () ->
                                ticket_id = parseInt($(this).attr('data-id'))
                                Bazaarboy.post 'event/promo/unlink/', {id:promo_id, ticket:ticket_id}, (response) ->
                                    if response.status isnt 'OK'
                                        alert response.message
                            $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket.selected').each () ->
                                ticket_id = parseInt($(this).attr('data-id'))
                                Bazaarboy.post 'event/promo/link/', {id:promo_id, ticket:ticket_id}, (response) ->
                                    if response.status isnt 'OK'
                                        alert response.message
                                    linkedTickets++
                                    if linkedTickets == selectedTickets
                                        newPromo = $('div.promo-template').clone()
                                        newPromo.find('div.promo-name').html promo_code
                                        newPromo.find('div.promo-stats').html(amount_claimed + " Claimed")
                                        newPromo.attr('data-id', promo_id)
                                        newPromo.find('a.edit-promo').attr('data-id', promo_id)
                                        $('div.promo-template').after newPromo
                                        newPromo.removeClass 'promo-template'
                                        newPromo.removeClass 'hide'
                                        $('div#promos div.edit').fadeOut 300, () ->
                                            $('div#promos form#promo-form a.promo-type').removeClass 'active'
                                            $('div#promos form#promo-form a.promo-type').eq(0).addClass 'active'
                                            $('div#promos form#promo-form input').val ''
                                            $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass 'selected'
                                            $('div#promos div.content').fadeIn 300
                                        return
                                    return
                                return
                        else
                            alert response.message
                        return
            else
                alert 'Must Select At Least One Ticket'
        return
    init: () ->
        scope = this
        $('body').on 'click', 'a.add-custom-field-btn', () ->
            newField = $('div.custom-fields-container div.custom-field-container.template').clone()
            $('div.custom-fields-container').prepend(newField)
            newField.removeClass 'hide'
            newField.removeClass 'template'
            return
        $('a.new-ticket').click () =>
            @newTicket()
            return
        $('input#ticket-time-range').change () ->
          if $(this).is(':checked')
            $('div.time-range-inputs').removeClass 'hide'
          else
            $('div.time-range-inputs').addClass 'hide'
          return
        #MOVE TICKET START
        $('body').on 'click', 'a.move-ticket-btn', () ->
            if not scope.reordering or true
                scope.reordering = true
                thisButton = $(this)
                originalHTML = thisButton.html()
                thisButton.html 'Moving...'
                thisTicket = $(this).parents('.ticket-option')
                if $(this).hasClass 'move-ticket-up'
                    swapTicket = thisTicket.prev('.ticket-option')
                    swapTicket.before(thisTicket)
                if $(this).hasClass 'move-ticket-down'
                    swapTicket = thisTicket.next('.ticket-option')
                    swapTicket.after(thisTicket)
                params = 
                    event: eventId
                    details: {}
                $('.ticket-option:not(.template)').each () ->
                    $(this).find('.move-ticket-up').parent().removeClass 'hide'
                    $(this).find('.move-ticket-down').parent().removeClass 'hide'
                    if $(this).index() is 0
                        $(this).find('.move-ticket-up').parent().addClass 'hide'
                    if $(this).index() is ($('.ticket-option:not(.template)').length - 1)
                        $(this).find('.move-ticket-down').parent().addClass 'hide'
                    params.details[$(this).data('id')] = $(this).index()
                    return
                params.details = JSON.stringify params.details
                Bazaarboy.post 'event/tickets/reorder/', params, (response) =>
                    if response.status isnt 'OK'
                        alert response.message
                    else
                        console.log response
                    thisButton.html originalHTML
                    scope.reordering = false
                    return
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
                scope.ticketSubmitting = true
                isNew = $('div#edit-ticket').hasClass 'add'
                ticketId = $('div#edit-ticket').attr 'data-id'
                params = $(this).serializeObject()
                if $('div#edit-ticket form input[name=request_address]').is(':checked')
                    params.request_address = true
                else
                    params.request_address = false
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
                extraFields = {}
                $('div.custom-field-container:not(.template)').each () ->
                    fieldName = $(this).find('input.field_name').val()
                    fieldOptions = $(this).find('input.field_options').val()
                    if fieldName.trim() isnt ''
                        extraFields[fieldName] = fieldOptions
                    return
                params.extra_fields = JSON.stringify extraFields
                endpoint = 'event/ticket/edit/'
                if isNew
                    endpoint = 'event/ticket/create/'
                if params.name.trim() != '' and params.description.trim() != ''
                    console.log params
                    Bazaarboy.post endpoint, params, (response) ->
                        if response.status is 'OK'
                            $('div#event-modify-tickets div.empty-state-container').addClass 'hide'
                            $('div#event-modify-tickets div#action-canvas').removeClass 'hide'
                            ticketOption = null
                            if isNew
                                ticketOption = $('div.templates div.ticket-option').clone()
                                $(ticketOption).attr 'data-id', response.ticket.pk
                                $(ticketOption).prependTo 'div#ticket-canvas'
                                $(ticketOption).find('.move-ticket-up').parent().addClass 'hide'
                                $(ticketOption).next('.ticket-option').find('.move-ticket-up').parent().removeClass 'hide'
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
                            console.log response
                            $(ticketOption).find('span.sold').html sold
                            quantity = if response.ticket.quantity then '/' + response.ticket.quantity else ''
                            $(ticketOption).find('span.quantity').html quantity
                            wording = 'RSVP\'d'
                            wordingObject = 'RSVPs'
                            if response.ticket.price > 0
                                if isNew
                                  $('div#event-modify-tickets div#promos').removeClass 'hide'
                                  newPromosTicket = $('div.promo-form-ticket.template').clone()
                                  newPromosTicket.find('a.select-ticket').attr('data-id', response.ticket.pk)
                                  newPromosTicket.find('a.select-ticket').html response.ticket.name + ' ($' + response.ticket.price + ')'
                                  newPromosTicket.removeClass 'hide'
                                  newPromosTicket.removeClass 'template'
                                  $('div.promo-form-tickets').append(newPromosTicket)
                                wording = 'Sold'
                                wordingObject = 'Ticket Holders'
                            $(ticketOption).find('span.wording').html wording
                            $(ticketOption).find('span.wording-object').html wordingObject
                            $('div#edit-ticket').fadeOut 300, () ->
                                scope.ticketSubmitting = false
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
                        $(ticketOption).find('input[name=ticket]').val(response.ticket.pk)
                        $('div#edit-ticket').fadeOut 300, () ->
                            scope.ticketSubmitting = false
                            if response.status isnt 'OK'
                                alert response.message
                        return
                else
                    scope.ticketSubmitting = false
                    if params.name.trim() == ''
                        $('div#edit-ticket input[name=name]').addClass('warning')
                    if params.description.trim() == ''
                        $('div#edit-ticket textarea[name=description]').addClass('warning')
            return
        $('div#edit-ticket input[name=name], div#edit-ticket textarea[name=description]').keypress () ->
            if $(this).val().trim() != ''
                $(this).removeClass('warning')
            return
        # PROMO CODES
        # Date auto-complete
        $('form#promo-form').find('input[name=promo_start_time]').pikaday
            format: 'MM/DD/YYYY'
            onSelect: () ->
                $('form#promo-form').find('input[name=expiration_time]').pikaday 'gotoDate', this.getDate()
                $('form#promo-form').find('input[name=expiration_time]').pikaday 'setMinDate', this.getDate()
                return
        $('form#promo-form').find('input[name=expiration_time]').pikaday
            format: 'MM/DD/YYYY'
        $('div#promos div.new-promo-controls a.save-promo').click () ->
            scope.savePromo(true)
            return
        $('div#promos div.edit-promo-controls a.save-promo').click () ->
            scope.savePromo(false)
            return
        $('div#promos').on 'click', 'a.add-promo',  () ->
            $('div#promos form#promo-form a.promo-type').removeClass 'active'
            $('div#promos form#promo-form a.promo-type').eq(0).addClass 'active'
            $('div#promos form#promo-form input').val ''
            $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass 'selected'
            $('div#promos div.edit div.title').html 'Add Promo Code'
            $('div#promos div.new-promo-controls').removeClass 'hide'
            $('div#promos div.edit-promo-controls').addClass 'hide'
            $('div#promos form#promo-form span.discount-identifier').html '($)'
            $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Amount (between $0 and price of ticket)')
            $('div#promos div.content').fadeOut 300, () ->
                $('div#promos div.edit').fadeIn 300
                return
            return
        $('div#promos').on 'click', 'a.edit-promo',  () ->
            $('form#promo-form').attr('data-id', $(this).attr('data-id'))
            $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass 'selected'
            Bazaarboy.get 'event/promo/', {id: parseInt($(this).attr('data-id'))}, (response) ->
                promo = response.promo
                console.log promo
                tickets = promo.tickets
                $('div#promos div.edit div.title').html 'Edit Promo Code: ' + promo.code
                $('div#promos div.new-promo-controls').addClass 'hide'
                $('div#promos div.edit-promo-controls').removeClass 'hide'
                $('form#promo-form input[name=code]').val promo.code
                $('form#promo-form a.promo-type').removeClass 'active'
                if promo.amount
                    $('form#promo-form a.promo-type').eq(0).addClass 'active'
                    $('form#promo-form input[name=discount]').val promo.amount
                    $('div#promos form#promo-form span.discount-identifier').html '($)'
                    $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Amount (between $0 and price of ticket)')
                else
                    $('form#promo-form a.promo-type').eq(1).addClass 'active'
                    $('form#promo-form input[name=discount]').val(promo.discount*100)
                    $('div#promos form#promo-form span.discount-identifier').html '(%)'
                    $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Percentage (1-100)')
                $('form#promo-form input[name=email_domain]').val promo.email_domain
                if promo.quantity
                    $('form#promo-form input[name=quantity]').val promo.quantity
                else
                    $('form#promo-form input[name=quantity]').val ''
                if promo.start_time
                    $('form#promo-form input[name=promo_start_time]').val promo.start_time
                else
                    $('form#promo-form input[name=promo_start_time]').val ''
                if promo.expiration_time
                    $('form#promo-form input[name=expiration_time]').val promo.expiration_time
                else
                    $('form#promo-form input[name=expiration_time]').val ''
                $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').each () ->
                    if tickets.indexOf(parseInt($(this).attr('data-id'))) > -1
                        $(this).addClass 'selected'
                    return
                $('div#promos div.content').fadeOut 300, () ->
                    $('div#promos div.edit').fadeIn 300
                    return
                return
            return
        $('div#promos').on 'click', 'a.cancel-promo',  () ->
            $('div#promos div.edit').fadeOut 300, () ->
                $('div#promos div.content').fadeIn 300
                return
            return
        $('div#promos').on 'click', 'a.delete-promo',  () ->
            Bazaarboy.get 'event/promo/', {id: parseInt($('form#promo-form').attr('data-id'))}, (response) ->
                if confirm("Are you sure you want to delete the promo code: '" + response.promo.code + "'?")
                    Bazaarboy.post 'event/promo/delete/', {id: parseInt($('form#promo-form').attr('data-id'))}, (response) ->
                        if response.status is 'OK'
                            $("div.promo").each () ->
                                if parseInt($(this).attr('data-id')) is parseInt($('form#promo-form').attr('data-id'))
                                    $(this).remove()
                                return
                            $('div#promos div.edit').fadeOut 300, () ->
                                $('div#promos div.content').fadeIn 300
                        else
                            alert response.message
                        return
                return
            return
        $('div#promos form#promo-form a.promo-type').click () ->
            $('div#promos form#promo-form a.promo-type').removeClass 'active'
            $(this).addClass 'active'
            if $(this).attr('data-type') is 'number'
                $('div#promos form#promo-form span.discount-identifier').html '($)'
                $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Amount (between $0 and price of ticket)')
            else
                $('div#promos form#promo-form span.discount-identifier').html '(%)'
                $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Percentage (1-100)')
            return
        $('div#promos').on 'click', 'div.promo-form-tickets:not(.template) a.select-ticket', () ->
            $(this).toggleClass 'selected'
            return
        return

Bazaarboy.event.modify.tickets.init()