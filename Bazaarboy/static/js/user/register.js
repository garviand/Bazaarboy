(function() {
  this.Bazaarboy.user.register = {
    init: function() {
      $('form[name=register]').submit(function(event) {
        event.preventDefault();
      });
    },
    fbAuth: function(fbAccessToken, email, city) {
      if (email == null) {
        email = '';
      }
      if (city == null) {
        city = '';
      }
      console.log(city);
      Bazaarboy.post('user/fbAuth/', {
        fb_token: fbAccessToken,
        email: email,
        city: city
      }, function(response) {
        if (response.status === 'OK') {
          Bazaarboy.redirect('index');
        } else {
          alert(response.message);
        }
      });
    }
  };

  window.fbSDKReady = function() {
    return FB.getLoginStatus(function(response) {
      var fbAccessToken;
      if (response.status === 'connected') {
        fbAccessToken = response.authResponse.accessToken;
        $('a#fb_login').click(function() {
          var city, email;
          email = $('input[name=email]').val();
          city = $('input[name=city]').val();
          Bazaarboy.user.register.fbAuth(fbAccessToken, email, city);
        });
      } else {
        $('a#fb_login').click(function() {
          var city, email;
          email = $('input[name=email]').val();
          city = $('input[name=city]').val();
          FB.login(function(response) {
            if (response.authResponse) {
              fbAccessToken = response.authResponse.accessToken;
              Bazaarboy.user.register.fbAuth(fbAccessToken, email, city);
            }
          });
        });
      }
    });
  };

}).call(this);
