(function() {
  this.Bazaarboy.landing = {
    init: function() {
      $('form.login input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form.login').submit();
        }
      });
      $('form.login').submit(function(event) {
        var params;
        event.preventDefault();
        params = $('form.login').serializeObject();
        params = Bazaarboy.trim(params);
        if (params.email.length !== 0 && params.password.length !== 0) {
          Bazaarboy.get('user/auth/', params, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('index');
            } else {
              alert(response.message);
            }
          });
        }
      });
      $('form.register input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form.register').submit();
        }
      });
      $('form.register').submit(function(event) {
        var params;
        event.preventDefault();
        params = $('form.register').serializeObject();
        params = Bazaarboy.trim(params);
        if (params.email.length !== 0 && params.password.length !== 0 && params.password === params.confirm && params.first_name.length !== 0 && params.last_name.length !== 0) {
          Bazaarboy.post('user/create/', params, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('index');
            } else {
              alert(response.message);
            }
          });
        }
      });
    }
  };

  Bazaarboy.landing.init();

}).call(this);
