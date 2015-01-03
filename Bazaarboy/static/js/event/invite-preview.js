(function() {
  Bazaarboy.event.invite_preview = {
    sending: false,
    init: function() {
      var scope;
      scope = this;
      $('div.email-actions a.send-email').click(function() {
        var button, inviteId;
        if (!scope.sending) {
          button = $(this);
          button.html('Sending...');
          scope.sending = true;
          inviteId = $(this).data('id');
          Bazaarboy.post('event/invite/send/', {
            id: inviteId
          }, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('event/invite/' + response.invite.pk + '/details/');
            } else {
              swal(response.message);
              scope.sending = false;
              button.html('Send Email');
            }
          });
        }
      });
    }
  };

  Bazaarboy.event.invite_preview.init();

}).call(this);
