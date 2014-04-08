(function() {
  this.Bazaarboy.login = {
    init: function() {
      $('div#login div#footer a.switch').click(function() {
        if ($('div#login-container').hasClass('active')) {
          $('div#login div#footer a.switch').html('Login');
          $('div#login-container').fadeOut(300, function() {
            $('div#register-container').fadeIn(300, function() {
              $('div#login-container').removeClass('active');
              $('div#register-container').addClass('active');
            });
          });
        } else {
          $('div#login div#footer a.switch').html('Register');
          $('div#register-container').fadeOut(300, function() {
            $('div#login-container').fadeIn(300, function() {
              $('div#register-container').removeClass('active');
              $('div#login-container').addClass('active');
            });
          });
        }
      });
      $('form#login-form input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form#login-form').submit();
        }
      });
      $('form#login-form').submit(function(event) {
        var params;
        event.preventDefault();
        params = $('form#login-form').serializeObject();
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
      $('form#register-form input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form#register-form').submit();
        }
      });
      $('form#register-form').submit(function(event) {
        var params;
        event.preventDefault();
        params = $('form#register-form').serializeObject();
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

  Bazaarboy.login.init();

}).call(this);
