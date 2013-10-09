(function() {
  Bazaarboy.event.create = {
    init: function() {
      $('div#event_create form.create').submit(function(event) {
        var data, local_time, utc_time;
        event.preventDefault();
        data = $(this).serializeObject();
        local_time = moment(data['start_time']);
        utc_time = moment.utc(local_time);
        data['start_time'] = utc_time.format("YYYY-MM-DD HH:mm:ss");
        Bazaarboy.post('event/create/', data, function(response) {
          var eventUrl;
          if (response.status === 'OK') {
            eventUrl = 'event/' + response.event.pk;
            if (!loggedIn) {
              eventUrl += '?token=' + response.event.access_token;
            }
            Bazaarboy.redirect(eventUrl);
          } else {
            console.log(response);
          }
        });
      });
    }
  };

  Bazaarboy.event.create.init();

}).call(this);
