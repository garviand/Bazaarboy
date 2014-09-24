(function() {
  var fbSDKReady;

  this.Bazaarboy.user.login = {
    init: function() {
      $('form[name=login]').submit(function(event) {
        var params;
        event.preventDefault();
        params = $('form[name=login]').serialize();
        Bazaarboy.post('user/auth/', params, function(response) {
          if (response.status === 'OK') {
            return Bazaarboy.redirect('index');
          } else {
            return alert(response.message);
          }
        });
      });
    }
  };

  fbSDKReady = function() {
    return FB.getLoginStatus(function(response) {
      var fbAccessToken;
      if (response.status === 'connected') {
        fbAccessToken = response.authResponse.accessToken;
        return console.log(fbAccessToken);
      }
    });
  };

}).call(this);
