(function() {
  Bazaarboy.profile["new"] = {
    init: function() {
      $('form.profile-new').submit(function(event) {
        var optionals, params;
        event.preventDefault();
        params = $(this).serializeObject();
        optionals = ['email', 'phone', 'link_website', 'link_facebook', 'EIN'];
        params = Bazaarboy.stripEmpty(params, optionals);
        Bazaarboy.post('profile/create/', params, function(response) {
          if (response.status === 'OK') {
            Bazaarboy.redirect('index');
          } else {
            alert(response.message);
          }
        });
      });
    }
  };

  Bazaarboy.profile["new"].init();

}).call(this);
