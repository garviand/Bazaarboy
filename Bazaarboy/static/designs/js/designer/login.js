(function() {
  Bazaarboy.designs.designer.login = {
    init: function() {
      $("form#login-form").submit(function(e) {
        var params;
        e.preventDefault();
        params = {};
        params.email = $("form#login-form input[name=email]").val();
        params.password = $("form#login-form input[name=password]").val();
        if (params.email.length !== 0 && params.password.length !== 0) {
          return Bazaarboy.post('designs/designer/auth/', params, function(response) {
            if (response.status === 'OK') {
              return console.log('Logged In');
            } else {
              return alert('Failed');
            }
          });
        }
      });
    }
  };

  Bazaarboy.designs.designer.login.init();

}).call(this);
