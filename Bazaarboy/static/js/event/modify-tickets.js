(function() {
  Bazaarboy.event.modify.tickets = {
    ticketSubmitting: false,
    reordering: false,
    newTicket: function() {
      $('div.custom-field-container:not(.template)').remove();
      $('div#edit-ticket div.step-2').hide();
      $('div#edit-ticket div.step-1').show();
      $('div#edit-ticket').removeAttr('data-id').removeClass('edit').addClass('add');
      $('div#edit-ticket div.step-1').removeClass('hide');
      $('div#edit-ticket div.step-1 span.type').html('First, Choose a');
      $('div#edit-ticket div.step-2').addClass('hide');
      $('div#edit-ticket div.step-2 span.type').html('New');
      $('div#edit-ticket input').val('');
      $('div#edit-ticket textarea').val('');
      $('div#edit-ticket div.info a.blue-btn').parent().removeClass('columns').addClass('hide');
      $('div#edit-ticket div.info input.primary-btn').val('Add').parent().addClass('medium-centered').removeClass('end');
      this.initDateTimeAutoComplete($('div#edit-ticket form'));
      $('div#edit-ticket').fadeIn(300);
    },
    editTicket: function(ticket) {
      var _this = this;
      Bazaarboy.get('event/ticket/', {
        id: ticket
      }, function(response) {
        var endDate, endTime, extraFields, field_name, field_options, newField, quantity, startDate, startTime;
        if (response.status !== 'OK') {
          alert(response.message);
        } else {
          $('div.custom-field-container:not(.template)').remove();
          if (response.ticket.extra_fields.length > 0) {
            extraFields = response.ticket.extra_fields;
            console.log(extraFields);
            extraFields = JSON.parse(extraFields);
            for (field_name in extraFields) {
              field_options = extraFields[field_name];
              newField = $('div.custom-fields-container div.custom-field-container.template').clone();
              newField.find('input.field_name').val(field_name);
              newField.find('input.field_options').val(field_options);
              newField.removeClass('hide');
              newField.removeClass('template');
              $('div.add-custom-field-container').before(newField);
            }
          }
          $('div#edit-ticket').removeClass('add').addClass('edit');
          $('div#edit-ticket div.step-1').addClass('hide');
          $('div#edit-ticket div.step-1 span.type').html('Switch');
          $('div#edit-ticket div.step-2').removeClass('hide');
          $('div#edit-ticket div.step-2 span.type').html('Edit');
          $('div#edit-ticket input[name=name]').val(response.ticket.name);
          if (response.ticket.request_address) {
            $('div#edit-ticket input[name=request_address]').prop('checked', true);
          } else {
            $('div#edit-ticket input[name=request_address]').prop('checked', false);
          }
          if (response.ticket.price === 0) {
            $('div#edit-ticket div.price input').val(0);
            $('div#edit-ticket div.price').addClass('hide');
            $('div#edit-ticket div.quantity').removeClass('medium-6').addClass('medium-12');
          } else {
            $('div#edit-ticket input[name=price]').val(response.ticket.price);
            $('div#edit-ticket div.price').removeClass('hide');
            $('div#edit-ticket div.quantity').removeClass('medium-12').addClass('medium-6');
          }
          quantity = response.ticket.quantity != null ? response.ticket.quantity : '';
          $('div#edit-ticket input[name=quantity]').val(quantity);
          $('div#edit-ticket textarea[name=description]').val(response.ticket.description);
          startTime = '';
          startDate = '';
          if (response.ticket.start_time != null) {
            startTime = moment.utc(response.ticket.start_time, 'YYYY-MM-DD HH:mm:ss');
            startDate = startTime.local().format('MM/DD/YYYY');
            startTime = startTime.format('h:mm A');
          }
          $('div#edit-ticket textarea[name=start_date]').val(startDate);
          $('div#edit-ticket textarea[name=start_time]').val(startTime);
          endTime = '';
          endDate = '';
          if (response.ticket.end_time != null) {
            endTime = moment.utc(response.ticket.end_time, 'YYYY-MM-DD HH:mm:ss');
            endDate = endTime.local().format('MM/DD/YYYY');
            endTime = endTime.format('h:mm A');
          }
          $('div#edit-ticket textarea[name=end_date]').val(endDate);
          $('div#edit-ticket textarea[name=end_time]').val(endTime);
          _this.initDateTimeAutoComplete($('div#edit-ticket'));
          $('div#edit-ticket div.info a.blue-btn').parent().addClass('columns').removeClass('hide');
          $('div#edit-ticket div.info input.primary-btn').val('Save').parent().removeClass('medium-centered').addClass('end');
          $('div#edit-ticket').attr('data-id', ticket).fadeIn(300);
          $('body').animate({
            scrollTop: 0
          }, 300);
        }
      });
    },
    initDateTimeAutoComplete: function(form) {
      var originalEndTime, originalStartTime;
      originalStartTime = $(form).find('input[name=start_time]').val();
      originalEndTime = $(form).find('input[name=end_time]').val();
      $(form).find('input[name=start_time], input[name=end_time]').timeAutocomplete({
        blur_empty_populate: false,
        appendTo: '#menu-container'
      });
      $(form).find('input[name=start_time]').val(originalStartTime);
      $(form).find('input[name=end_time]').val(originalEndTime);
      $(form).find('input[name=start_date]').pikaday({
        format: 'MM/DD/YYYY',
        onSelect: function() {
          $(form).find('input[name=end_date]').pikaday('gotoDate', this.getDate());
          $(form).find('input[name=end_date]').pikaday('setMinDate', this.getDate());
        }
      });
      $(form).find('input[name=end_date]').pikaday({
        format: 'MM/DD/YYYY'
      });
    },
    savePromo: function(newPromo) {
      var failedLinks, linkedTickets, params, selectedTickets;
      if (!this.promoSubmitting) {
        params = $('form#promo-form').serializeObject();
        params.start_time = params.promo_start_time;
        params.event = eventId;
        if (params.start_time !== void 0 && params.start_time.trim().length !== 0) {
          params.start_time = moment(params.start_time.trim(), 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
          if (!params.start_time) {
            alert('Invalid Start Date');
          }
        } else if (params.start_time.trim().length === 0) {
          params.start_time = 'none';
        }
        if (params.expiration_time !== void 0 && params.expiration_time.trim().length !== 0) {
          params.expiration_time = moment(params.expiration_time.trim(), 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss');
          if (!params.expiration_time) {
            alert('Invalid Expiration Date');
          }
        } else if (params.expiration_time.trim().length === 0) {
          params.expiration_time = 'none';
        }
        if (isNaN(parseInt(params.discount))) {
          alert('Discount Amount Must Be A Number');
          return;
        }
        if ($('div#promos form#promo-form a.promo-type.active').attr('data-type') === 'number') {
          params.amount = parseInt(params.discount);
          params.discount = '';
        } else {
          params.discount = parseFloat(params.discount) / 100;
          if (params.discount > 1) {
            alert('Percentage Must Be Between 1 and 100');
            return;
          }
        }
        selectedTickets = $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket.selected').length;
        linkedTickets = 0;
        failedLinks = 0;
        if (selectedTickets > 0) {
          if (newPromo) {
            Bazaarboy.post('event/promo/create/', params, function(response) {
              var promo_code, promo_id;
              if (response.status === 'OK') {
                promo_id = response.promo.pk;
                promo_code = response.promo.code;
                $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket.selected').each(function() {
                  var ticket_id;
                  ticket_id = parseInt($(this).attr('data-id'));
                  Bazaarboy.post('event/promo/link/', {
                    id: promo_id,
                    ticket: ticket_id
                  }, function(response) {
                    if (response.status !== 'OK') {
                      alert(response.message);
                    }
                    linkedTickets++;
                    if (linkedTickets === selectedTickets) {
                      newPromo = $('div.promo-template').clone();
                      newPromo.find('div.promo-name').html(promo_code);
                      newPromo.attr('data-id', promo_id);
                      newPromo.find('a.edit-promo').attr('data-id', promo_id);
                      $('div.promo-template').after(newPromo);
                      newPromo.removeClass('promo-template');
                      newPromo.removeClass('hide');
                      $('div#promos div.edit').fadeOut(300, function() {
                        $('div#promos form#promo-form a.promo-type').removeClass('active');
                        $('div#promos form#promo-form a.promo-type').eq(0).addClass('active');
                        $('div#promos form#promo-form input').val('');
                        $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass('selected');
                        return $('div#promos div.content').fadeIn(300);
                      });
                      return;
                    }
                  });
                });
              } else {
                alert(response.message);
              }
            });
          } else {
            $("div.promo").each(function() {
              if (parseInt($(this).attr('data-id')) === parseInt($('form#promo-form').attr('data-id'))) {
                $(this).remove();
              }
            });
            params.id = $('form#promo-form').attr('data-id');
            params.id = parseInt(params.id);
            console.log(params);
            Bazaarboy.post('event/promo/edit/', params, function(response) {
              var amount_claimed, promo_code, promo_id;
              if (response.status === 'OK') {
                amount_claimed = response.claimed;
                promo_id = response.promo.pk;
                promo_code = response.promo.code;
                $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket:not(.selected)').each(function() {
                  var ticket_id;
                  ticket_id = parseInt($(this).attr('data-id'));
                  return Bazaarboy.post('event/promo/unlink/', {
                    id: promo_id,
                    ticket: ticket_id
                  }, function(response) {
                    if (response.status !== 'OK') {
                      return alert(response.message);
                    }
                  });
                });
                $('form#promo-form div.promo-form-tickets:not(.template) a.select-ticket.selected').each(function() {
                  var ticket_id;
                  ticket_id = parseInt($(this).attr('data-id'));
                  Bazaarboy.post('event/promo/link/', {
                    id: promo_id,
                    ticket: ticket_id
                  }, function(response) {
                    if (response.status !== 'OK') {
                      alert(response.message);
                    }
                    linkedTickets++;
                    if (linkedTickets === selectedTickets) {
                      newPromo = $('div.promo-template').clone();
                      newPromo.find('div.promo-name').html(promo_code);
                      newPromo.find('div.promo-stats').html(amount_claimed + " Claimed");
                      newPromo.attr('data-id', promo_id);
                      newPromo.find('a.edit-promo').attr('data-id', promo_id);
                      $('div.promo-template').after(newPromo);
                      newPromo.removeClass('promo-template');
                      newPromo.removeClass('hide');
                      $('div#promos div.edit').fadeOut(300, function() {
                        $('div#promos form#promo-form a.promo-type').removeClass('active');
                        $('div#promos form#promo-form a.promo-type').eq(0).addClass('active');
                        $('div#promos form#promo-form input').val('');
                        $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass('selected');
                        return $('div#promos div.content').fadeIn(300);
                      });
                      return;
                    }
                  });
                });
              } else {
                alert(response.message);
              }
            });
          }
        } else {
          alert('Must Select At Least One Ticket');
        }
      }
    },
    init: function() {
      var isEditTicketInAnimation, scope,
        _this = this;
      scope = this;
      $('body').on('click', 'a.add-custom-field-btn', function() {
        var newField;
        newField = $('div.custom-fields-container div.custom-field-container.template').clone();
        $('div.add-custom-field-container').before(newField);
        newField.removeClass('hide');
        newField.removeClass('template');
      });
      $('a.new-ticket').click(function() {
        _this.newTicket();
      });
      $('input#ticket-time-range').change(function() {
        if ($(this).is(':checked')) {
          $('div.time-range-inputs').removeClass('hide');
        } else {
          $('div.time-range-inputs').addClass('hide');
        }
      });
      $('body').on('click', 'a.move-ticket-btn', function() {
        var originalHTML, params, swapTicket, thisButton, thisTicket,
          _this = this;
        if (!scope.reordering || true) {
          scope.reordering = true;
          thisButton = $(this);
          originalHTML = thisButton.html();
          thisButton.html('Moving...');
          thisTicket = $(this).parents('.ticket-option');
          if ($(this).hasClass('move-ticket-up')) {
            swapTicket = thisTicket.prev('.ticket-option');
            swapTicket.before(thisTicket);
          }
          if ($(this).hasClass('move-ticket-down')) {
            swapTicket = thisTicket.next('.ticket-option');
            swapTicket.after(thisTicket);
          }
          params = {
            event: eventId,
            details: {}
          };
          $('.ticket-option:not(.template)').each(function() {
            $(this).find('.move-ticket-up').parent().removeClass('hide');
            $(this).find('.move-ticket-down').parent().removeClass('hide');
            if ($(this).index() === 0) {
              $(this).find('.move-ticket-up').parent().addClass('hide');
            }
            if ($(this).index() === ($('.ticket-option:not(.template)').length - 1)) {
              $(this).find('.move-ticket-down').parent().addClass('hide');
            }
            params.details[$(this).data('id')] = $(this).index();
          });
          params.details = JSON.stringify(params.details);
          Bazaarboy.post('event/tickets/reorder/', params, function(response) {
            if (response.status !== 'OK') {
              alert(response.message);
            } else {
              console.log(response);
            }
            thisButton.html(originalHTML);
            scope.reordering = false;
          });
        }
      });
      $('div.ticket-option div.top div.secondary-btn').click(function() {
        var ticket;
        ticket = $(this).closest('div.ticket-option').attr('data-id');
        scope.editTicket(ticket);
      });
      isEditTicketInAnimation = false;
      $('div#edit-ticket div.cancel-btn').click(function() {
        $('div#edit-ticket').fadeOut(300);
      });
      $('div#edit-ticket div.type a.action-btn').click(function() {
        var isFree;
        if (!isEditTicketInAnimation) {
          isFree = $(this).hasClass('free');
          if (isFree) {
            $('div#edit-ticket div.price input').val(0);
            $('div#edit-ticket div.price').addClass('hide');
            $('div#edit-ticket div.quantity').removeClass('medium-6').addClass('medium-12');
          } else {
            if (parseInt($('div#edit-ticket div.price input').val()) === 0) {
              $('div#edit-ticket div.price input').val('');
            }
            $('div#edit-ticket div.price').removeClass('hide');
            $('div#edit-ticket div.quantity').removeClass('medium-12').addClass('medium-6');
          }
          isEditTicketInAnimation = true;
          $('div#edit-ticket div.step-1').fadeOut(300, function() {
            $('div#edit-ticket div.step-2').fadeIn(300, function() {
              isEditTicketInAnimation = false;
            });
          });
        }
      });
      $('div#edit-ticket div.change-type').click(function() {
        isEditTicketInAnimation = true;
        $('div#edit-ticket div.step-2').fadeOut(300, function() {
          $('div#edit-ticket div.step-1').fadeIn(300, function() {
            isEditTicketInAnimation = false;
          });
        });
      });
      $('div#edit-ticket a.blue-btn').click(function() {
        var ticketId;
        ticketId = $('div#edit-ticket').attr('data-id');
        if (confirm('Are you sure you want to delete this ticket?')) {
          Bazaarboy.post('event/ticket/delete/', {
            id: ticketId
          }, function(response) {
            if (response.status !== 'OK') {
              alert(response.message);
            } else {
              isEditTicketInAnimation = true;
              $('div#edit-ticket').fadeOut(300, function() {
                $('div.ticket-option[data-id="' + ticketId + '"]').fadeOut(300, function() {
                  isEditTicketInAnimation = false;
                  $(this).remove();
                });
              });
            }
          });
        }
      });
      $('div#edit-ticket form').submit(function(event) {
        var endDate, endTime, endpoint, extraFields, isNew, params, startDate, startTime, ticketId;
        event.preventDefault();
        if (!scope.ticketSubmitting) {
          scope.ticketSubmitting = true;
          isNew = $('div#edit-ticket').hasClass('add');
          ticketId = $('div#edit-ticket').attr('data-id');
          params = $(this).serializeObject();
          if ($('div#edit-ticket form input[name=request_address]').is(':checked')) {
            params.request_address = true;
          } else {
            params.request_address = false;
          }
          if (isNew) {
            params.event = eventId;
          } else {
            params.id = ticketId;
          }
          if (params.quantity.trim().length === 0) {
            if (isNew) {
              delete params.quantity;
            } else {
              params.quantity = 'None';
            }
          }
          if (params.start_date.trim().length !== 0 && params.start_time.trim().length !== 0) {
            startDate = moment(params.start_date.trim(), 'MM/DD/YYYY');
            if (!startDate.isValid()) {
              return;
            }
            startTime = moment(params.start_time.trim(), 'h:mm A');
            if (!startTime.isValid()) {
              return;
            }
            params.start_time = moment(params.start_date.trim() + ' ' + params.start_time.trim(), 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss');
          } else {
            if (isNew) {
              delete params.start_time;
            } else {
              params.start_time = 'None';
            }
          }
          if (params.end_date.trim().length !== 0 && params.end_time.trim().length !== 0) {
            endDate = moment(params.end_date.trim(), 'MM/DD/YYYY');
            if (!endDate.isValid()) {
              return;
            }
            endTime = moment(params.end_time.trim(), 'h:mm A');
            if (!endTime.isValid()) {
              return;
            }
            params.end_time = moment(params.end_date.trim() + ' ' + params.end_time.trim(), 'MM/DD/YYYY h:mm A').utc().format('YYYY-MM-DD HH:mm:ss');
          } else {
            if (isNew) {
              delete params.end_time;
            } else {
              params.end_time = 'None';
            }
          }
          extraFields = {};
          $('div.custom-field-container:not(.template)').each(function() {
            var fieldName, fieldOptions;
            fieldName = $(this).find('input.field_name').val();
            fieldOptions = $(this).find('input.field_options').val();
            if (fieldName.trim() !== '') {
              extraFields[fieldName] = fieldOptions;
            }
          });
          params.extra_fields = JSON.stringify(extraFields);
          console.log(params.extra_fields);
          endpoint = 'event/ticket/edit/';
          if (isNew) {
            endpoint = 'event/ticket/create/';
          }
          if (params.name.trim() !== '' && params.description.trim() !== '') {
            Bazaarboy.post(endpoint, params, function(response) {
              var newPromosTicket, price, quantity, sold, ticketOption, wording, wordingObject;
              if (response.status === 'OK') {
                $('div#event-modify-tickets div.empty-state-container').addClass('hide');
                $('div#event-modify-tickets div#action-canvas').removeClass('hide');
                ticketOption = null;
                if (isNew) {
                  ticketOption = $('div.templates div.ticket-option').clone();
                  $(ticketOption).attr('data-id', response.ticket.pk);
                  $(ticketOption).prependTo('div#ticket-canvas');
                  $(ticketOption).find('.move-ticket-up').parent().addClass('hide');
                  $(ticketOption).next('.ticket-option').find('.move-ticket-up').parent().removeClass('hide');
                  $(ticketOption).find('div.top div.secondary-btn').click(function() {
                    var ticket;
                    ticket = $(this).closest('div.ticket-option').attr('data-id');
                    scope.editTicket(ticket);
                  });
                } else {
                  ticketOption = $('div.ticket-option[data-id="' + ticketId + '"]');
                }
                price = response.ticket.price > 0 ? '$' + response.ticket.price.toFixed(2) : 'Free';
                $(ticketOption).find('div.price').html(price);
                $(ticketOption).find('div.name').html(response.ticket.name);
                $(ticketOption).find('div.description').html(response.ticket.description);
                sold = response.ticket.sold != null ? response.ticket.sold : 0;
                console.log(response);
                $(ticketOption).find('span.sold').html(sold);
                quantity = response.ticket.quantity ? '/' + response.ticket.quantity : '';
                $(ticketOption).find('span.quantity').html(quantity);
                wording = 'RSVP\'d';
                wordingObject = 'RSVPs';
                if (response.ticket.price > 0) {
                  if (isNew) {
                    $('div#event-modify-tickets div#promos').removeClass('hide');
                    newPromosTicket = $('div.promo-form-ticket.template').clone();
                    newPromosTicket.find('a.select-ticket').attr('data-id', response.ticket.pk);
                    newPromosTicket.find('a.select-ticket').html(response.ticket.name + ' ($' + response.ticket.price + ')');
                    newPromosTicket.removeClass('hide');
                    newPromosTicket.removeClass('template');
                    $('div.promo-form-tickets').append(newPromosTicket);
                  }
                  wording = 'Sold';
                  wordingObject = 'Ticket Holders';
                }
                $(ticketOption).find('span.wording').html(wording);
                $(ticketOption).find('span.wording-object').html(wordingObject);
                $('div#edit-ticket').fadeOut(300, function() {
                  scope.ticketSubmitting = false;
                });
                price = response.ticket.price > 0 ? '$' + response.ticket.price.toFixed(2) : 'Free';
                $(ticketOption).find('div.price').html(price);
                $(ticketOption).find('div.name').html(response.ticket.name);
                $(ticketOption).find('div.description').html(response.ticket.description);
                sold = response.ticket.sold != null ? response.ticket.sold : 0;
                $(ticketOption).find('span.sold').html(sold);
                quantity = response.ticket.quantity ? '/' + response.ticket.quantity : '';
                $(ticketOption).find('span.quantity').html(quantity);
                wording = 'RSVP\'d';
                wordingObject = 'RSVPs';
                if (response.ticket.price > 0) {
                  wording = 'Sold';
                  wordingObject = 'Ticket Holders';
                }
                $(ticketOption).find('span.wording').html(wording);
                $(ticketOption).find('span.wording-object').html(wordingObject);
                $(ticketOption).find('input[name=ticket]').val(response.ticket.pk);
                $('div#edit-ticket').fadeOut(300, function() {
                  scope.ticketSubmitting = false;
                  if (response.status !== 'OK') {
                    return alert(response.message);
                  }
                });
              } else {
                scope.ticketSubmitting = false;
                alert(response.message);
              }
            });
          } else {
            scope.ticketSubmitting = false;
            if (params.name.trim() === '') {
              $('div#edit-ticket input[name=name]').addClass('warning');
            }
            if (params.description.trim() === '') {
              $('div#edit-ticket textarea[name=description]').addClass('warning');
            }
          }
        }
      });
      $('div#edit-ticket input[name=name], div#edit-ticket textarea[name=description]').keypress(function() {
        if ($(this).val().trim() !== '') {
          $(this).removeClass('warning');
        }
      });
      $('form#promo-form').find('input[name=promo_start_time]').pikaday({
        format: 'MM/DD/YYYY',
        onSelect: function() {
          $('form#promo-form').find('input[name=expiration_time]').pikaday('gotoDate', this.getDate());
          $('form#promo-form').find('input[name=expiration_time]').pikaday('setMinDate', this.getDate());
        }
      });
      $('form#promo-form').find('input[name=expiration_time]').pikaday({
        format: 'MM/DD/YYYY'
      });
      $('div#promos div.new-promo-controls a.save-promo').click(function() {
        scope.savePromo(true);
      });
      $('div#promos div.edit-promo-controls a.save-promo').click(function() {
        scope.savePromo(false);
      });
      $('div#promos').on('click', 'a.add-promo', function() {
        $('div#promos form#promo-form a.promo-type').removeClass('active');
        $('div#promos form#promo-form a.promo-type').eq(0).addClass('active');
        $('div#promos form#promo-form input').val('');
        $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass('selected');
        $('div#promos div.edit div.title').html('Add Promo Code');
        $('div#promos div.new-promo-controls').removeClass('hide');
        $('div#promos div.edit-promo-controls').addClass('hide');
        $('div#promos form#promo-form span.discount-identifier').html('($)');
        $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Amount (between $0 and price of ticket)');
        $('div#promos div.content').fadeOut(300, function() {
          $('div#promos div.edit').fadeIn(300);
        });
      });
      $('div#promos').on('click', 'a.edit-promo', function() {
        $('form#promo-form').attr('data-id', $(this).attr('data-id'));
        $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').removeClass('selected');
        Bazaarboy.get('event/promo/', {
          id: parseInt($(this).attr('data-id'))
        }, function(response) {
          var promo, tickets;
          promo = response.promo;
          console.log(promo);
          tickets = promo.tickets;
          $('div#promos div.edit div.title').html('Edit Promo Code: ' + promo.code);
          $('div#promos div.new-promo-controls').addClass('hide');
          $('div#promos div.edit-promo-controls').removeClass('hide');
          $('form#promo-form input[name=code]').val(promo.code);
          $('form#promo-form a.promo-type').removeClass('active');
          if (promo.amount) {
            $('form#promo-form a.promo-type').eq(0).addClass('active');
            $('form#promo-form input[name=discount]').val(promo.amount);
            $('div#promos form#promo-form span.discount-identifier').html('($)');
            $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Amount (between $0 and price of ticket)');
          } else {
            $('form#promo-form a.promo-type').eq(1).addClass('active');
            $('form#promo-form input[name=discount]').val(promo.discount * 100);
            $('div#promos form#promo-form span.discount-identifier').html('(%)');
            $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Percentage (1-100)');
          }
          $('form#promo-form input[name=email_domain]').val(promo.email_domain);
          if (promo.quantity) {
            $('form#promo-form input[name=quantity]').val(promo.quantity);
          } else {
            $('form#promo-form input[name=quantity]').val('');
          }
          if (promo.start_time) {
            $('form#promo-form input[name=promo_start_time]').val(promo.start_time);
          } else {
            $('form#promo-form input[name=promo_start_time]').val('');
          }
          if (promo.expiration_time) {
            $('form#promo-form input[name=expiration_time]').val(promo.expiration_time);
          } else {
            $('form#promo-form input[name=expiration_time]').val('');
          }
          $('div#promos div.promo-form-tickets:not(.template) a.select-ticket').each(function() {
            if (tickets.indexOf(parseInt($(this).attr('data-id'))) > -1) {
              $(this).addClass('selected');
            }
          });
          $('div#promos div.content').fadeOut(300, function() {
            $('div#promos div.edit').fadeIn(300);
          });
        });
      });
      $('div#promos').on('click', 'a.cancel-promo', function() {
        $('div#promos div.edit').fadeOut(300, function() {
          $('div#promos div.content').fadeIn(300);
        });
      });
      $('div#promos').on('click', 'a.delete-promo', function() {
        Bazaarboy.get('event/promo/', {
          id: parseInt($('form#promo-form').attr('data-id'))
        }, function(response) {
          if (confirm("Are you sure you want to delete the promo code: '" + response.promo.code + "'?")) {
            Bazaarboy.post('event/promo/delete/', {
              id: parseInt($('form#promo-form').attr('data-id'))
            }, function(response) {
              if (response.status === 'OK') {
                $("div.promo").each(function() {
                  if (parseInt($(this).attr('data-id')) === parseInt($('form#promo-form').attr('data-id'))) {
                    $(this).remove();
                  }
                });
                $('div#promos div.edit').fadeOut(300, function() {
                  return $('div#promos div.content').fadeIn(300);
                });
              } else {
                alert(response.message);
              }
            });
          }
        });
      });
      $('div#promos form#promo-form a.promo-type').click(function() {
        $('div#promos form#promo-form a.promo-type').removeClass('active');
        $(this).addClass('active');
        if ($(this).attr('data-type') === 'number') {
          $('div#promos form#promo-form span.discount-identifier').html('($)');
          $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Amount (between $0 and price of ticket)');
        } else {
          $('div#promos form#promo-form span.discount-identifier').html('(%)');
          $('div#promos form#promo-form input.discount-input').attr('placeholder', 'Discount Percentage (1-100)');
        }
      });
      $('div#promos').on('click', 'div.promo-form-tickets:not(.template) a.select-ticket', function() {
        $(this).toggleClass('selected');
      });
    }
  };

  Bazaarboy.event.modify.tickets.init();

}).call(this);
