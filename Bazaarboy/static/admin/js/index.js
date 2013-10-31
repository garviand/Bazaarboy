(function() {
  Bazaarboy.admin.login = {
    init: function() {}
  };

  $('.profile_login .profile_choices a').click(function(event) {
    var id;
    id = $(this).data('id');
    Bazaarboy.get('admin/login/profile', {
      id: id
    }, function(response) {
      if (response.status === 'OK') {
        Bazaarboy.redirect('index');
      } else {
        alert(response.message);
      }
    });
  });

  return;

}).call(this);
