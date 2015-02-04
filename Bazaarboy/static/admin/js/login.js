(function() {
  Bazaarboy.admin.login = {
    init: function() {
      $(document).ready(function() {
        $('form[name=login]').submit(function(event) {
          var params;
          event.preventDefault();
          if ($('form[name=login] input[name=name]').val().length === 0 || $('form[name=login] input[name=password]').val().length === 0) {
            return;
          }
          params = $('form[name=login]').serialize();
          Bazaarboy.get('admin/auth/', params, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('admin/');
            } else {
              $('form[name=login] a.btn').addClass('btn-danger');
              $('form[name=login] a.btn').html('Access Denied');
            }
          });
        });
        $('form[name=login] a.btn').click(function() {
          $('form[name=login]').submit();
        });
        $('form[name=login] input').keyup(function(event) {
          if (event.keyCode === 13) {
            event.preventDefault();
            $('form[name=login]').submit();
          } else {
            $('form[name=login] a.btn').removeClass('btn-danger');
            $('form[name=login] a.btn').html('Login');
          }
        });
      });
    }
  };

  Bazaarboy.admin.login.init();

}).call(this);
