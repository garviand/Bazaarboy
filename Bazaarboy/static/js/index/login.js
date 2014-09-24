(function() {
  this.Bazaarboy.login = {
    timer: void 0,
    rotateLogo: function(degree) {
      var _this = this;
      $('div.logo-small').css({
        WebkitTransform: 'rotate(' + degree + 'deg)'
      });
      $('div.logo-small').css({
        '-moz-transform': 'rotate(' + degree + 'deg)'
      });
      this.timer = setTimeout((function() {
        _this.rotateLogo(++degree);
      }), 5);
    },
    init: function() {
      var scope;
      scope = this;
      $('form#login-form input').keypress(function(event) {
        if (event.which === 13) {
          event.preventDefault();
          $('form#login-form').submit();
        }
      });
      $('form#login-form').submit(function(event) {
        var params;
        event.preventDefault();
        scope.rotateLogo(0);
        params = $('form#login-form').serializeObject();
        params = Bazaarboy.trim(params);
        if (params.email.length !== 0 && params.password.length !== 0) {
          Bazaarboy.post('user/auth/', params, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('index');
            } else {
              alert(response.message);
              window.clearTimeout(scope.timer);
              $('div.logo-small').css({
                WebkitTransform: 'none'
              });
              $('div.logo-small').css({
                '-moz-transform': 'none'
              });
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
        console.log('Submit Register Form');
        event.preventDefault();
        scope.rotateLogo(0);
        params = $('form#register-form').serializeObject();
        params = Bazaarboy.trim(params);
        if (params.email.length !== 0 && params.password.length !== 0 && params.password === params.confirm && params.first_name.length !== 0 && params.last_name.length !== 0) {
          Bazaarboy.post('user/create/', params, function(response) {
            console.log(response);
            if (response.status === 'OK') {
              Bazaarboy.redirect('index');
            } else {
              alert(response.message);
              window.clearTimeout(scope.timer);
              $('div.logo-small').css({
                WebkitTransform: 'none'
              });
              $('div.logo-small').css({
                '-moz-transform': 'none'
              });
            }
          });
        } else if (params.password !== params.confirm) {
          alert("Passwords do not match");
          window.clearTimeout(scope.timer);
          $('div.logo-small').css({
            WebkitTransform: 'none'
          });
          $('div.logo-small').css({
            '-moz-transform': 'none'
          });
        } else {
          alert("All fields must be filled out");
          window.clearTimeout(scope.timer);
          $('div.logo-small').css({
            WebkitTransform: 'none'
          });
          $('div.logo-small').css({
            '-moz-transform': 'none'
          });
        }
      });
    }
  };

  Bazaarboy.login.init();

}).call(this);
