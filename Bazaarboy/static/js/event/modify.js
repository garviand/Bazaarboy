(function() {
  Bazaarboy.event.modify = {
    switchLaunchState: function(eventId) {
      var _this = this;
      if ($('div#wrapper-sidebar div.launch-event').hasClass('launched')) {
        if (confirm('Are you sure you want to take the event offline?')) {
          Bazaarboy.post('event/delaunch/', {
            id: eventId
          }, function(response) {
            if (response.status === 'OK') {
              $('div#wrapper-sidebar div.launch-event').removeClass('launched').find('.launch-text').html('Publish Event');
            } else {
              alert(response.message);
            }
          });
        }
      } else {
        Bazaarboy.post('event/launch/', {
          id: eventId
        }, function(response) {
          if (response.status === 'OK') {
            $('div#wrapper-sidebar div.launch-event').addClass('launched').find('.launch-text').html('Take Offline');
          } else {
            alert(response.message);
          }
        });
      }
    },
    init: function() {
      var _this = this;
      $('div#wrapper-sidebar div.launch-event').click(function() {
        _this.switchLaunchState($('div#wrapper-sidebar div.launch-event').data('event-id'));
      });
    }
  };

  Bazaarboy.event.modify.init();

}).call(this);
