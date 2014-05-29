(function() {
  Bazaarboy.event.modify.tickets = {
    ticketSubmitting: false,
    newTicket: function() {
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
        var endDate, endTime, quantity, startDate, startTime;
        if (response.status !== 'OK') {
          alert(response.message);
        } else {
          $('div#edit-ticket').removeClass('add').addClass('edit');
          $('div#edit-ticket div.step-1').addClass('hide');
          $('div#edit-ticket div.step-1 span.type').html('Switch');
          $('div#edit-ticket div.step-2').removeClass('hide');
          $('div#edit-ticket div.step-2 span.type').html('Edit');
          $('div#edit-ticket input[name=name]').val(response.ticket.name);
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
    newPromo: function() {},
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
    init: function() {
      var isEditTicketInAnimation, scope,
        _this = this;
      scope = this;
      $('a.new-ticket').click(function() {
        _this.newTicket();
      });
      $('body').on('click', 'a.add-promo', function() {
        $(this).fadeOut(300, function() {
          $(this).parents('div.add-promo-container').find('div.add-promo-fields').fadeIn(300);
        });
      });
      $('body').on('submit', 'form.add-promo', function(e) {
        var form, params;
        e.preventDefault();
        params = $(this).serializeObject();
        form = $(this);
        Bazaarboy.post('event/promo/create/', params, function(response) {
          console.log(response);
          if (response.status === 'OK') {
            return form.parents('div.add-promo-fields').fadeOut(300, function() {
              form.find('input[type=text]').val('');
              return form.parents('div.add-promo-container').find('a.add-promo').fadeIn(300);
            });
          } else {
            return form.find('span.promo-error').html(response.message);
          }
        });
      });
      $('body').on('click', 'form.add-promo a.cancel-btn', function() {
        $(this).parents('div.add-promo-fields').fadeOut(300, function() {
          $(this).find('input[type=text]').val('');
          $('span.promo-error').html('&nbsp;');
          $(this).parents('div.add-promo-container').find('a.add-promo').fadeIn(300);
        });
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
        var endDate, endTime, endpoint, isNew, params, startDate, startTime, ticketId;
        event.preventDefault();
        if (!scope.ticketSubmitting) {
          console.log(scope.ticketSubmitting);
          scope.ticketSubmitting = true;
          isNew = $('div#edit-ticket').hasClass('add');
          ticketId = $('div#edit-ticket').attr('data-id');
          params = $(this).serializeObject();
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
          endpoint = 'event/ticket/edit/';
          if (isNew) {
            endpoint = 'event/ticket/create/';
          }
          Bazaarboy.post(endpoint, params, function(response) {
            var price, quantity, sold, ticketOption, wording, wordingObject;
            if (response.status === 'OK') {
              $('div#event-modify-tickets div.empty-state-container').addClass('hide');
              $('div#event-modify-tickets div#action-canvas').removeClass('hide');
              ticketOption = null;
              if (isNew) {
                ticketOption = $('div.templates div.ticket-option').clone();
                $(ticketOption).attr('data-id', response.ticket.pk);
                $(ticketOption).appendTo('div#ticket-canvas');
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
              });
            } else {
              scope.ticketSubmitting = false;
              alert(response.message);
            }
          });
        }
      });
    }
  };

  Bazaarboy.event.modify.tickets.init();

}).call(this);
