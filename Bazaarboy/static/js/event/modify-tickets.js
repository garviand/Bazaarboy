(function() {
  Bazaarboy.event.modify.tickets = {
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
      var isAddTicketInAnimation;
      this.initDateTimeAutoComplete($('div#add-ticket form'));
      isAddTicketInAnimation = false;
      $('div#add-ticket div.type a.action-btn').click(function() {
        var isFree;
        if (!isAddTicketInAnimation) {
          isFree = $(this).hasClass('free');
          if (isFree) {
            $('div#add-ticket div.price input').val(0);
            $('div#add-ticket div.price').addClass('hide');
            $('div#add-ticket div.quantity').removeClass('medium-6').addClass('medium-12');
          } else {
            if (parseInt($('div#add-ticket div.price input').val()) === 0) {
              $('div#add-ticket div.price input').val('');
            }
            $('div#add-ticket div.price').removeClass('hide');
            $('div#add-ticket div.quantity').removeClass('medium-12').addClass('medium-6');
          }
          isAddTicketInAnimation = true;
          $('div#add-ticket div.step-1').fadeOut(300, function() {
            $('div#add-ticket div.step-2').fadeIn(300, function() {
              isAddTicketInAnimation = false;
            });
          });
        }
      });
      $('div#add-ticket div.change-type').click(function() {
        isAddTicketInAnimation = true;
        $('div#add-ticket div.step-2').fadeOut(300, function() {
          $('div#add-ticket div.step-1').fadeIn(300, function() {
            isAddTicketInAnimation = false;
          });
        });
      });
      $('div#add-ticket form').submit(function(event) {
        var endDate, endTime, params, startDate, startTime;
        event.preventDefault();
        params = $(this).serializeObject();
        params.event = eventId;
        if (params.quantity.trim().length === 0) {
          delete params.quantity;
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
          delete params.start_time;
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
          delete params.end_time;
        }
        Bazaarboy.post('event/ticket/create/', params, function(response) {
          if (response.status === 'OK') {
            $('div#add-ticket').fadeOut(300);
          } else {
            alert(response.message);
          }
        });
      });
    }
  };

  Bazaarboy.event.modify.tickets.init();

}).call(this);
