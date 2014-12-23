(function() {
  Bazaarboy.event.invite = {
    saving: false,
    init: function() {
      var scope;
      scope = this;
      $('a.save-invite').click(function() {
        var details, eventId, lists, message;
        if (!scope.saving) {
          scope.saving = true;
          eventId = $('div.email input[name=event]').val();
          message = $('div.email textarea[name=message]').val();
          if (message.trim() === '') {
            swal("Wait!", "Email Message Cannot Be Empty", "warning");
            scope.saving = false;
            return;
          }
          details = $('div.email textarea[name=details]').val();
          lists = '1';
          console.log(eventId, message, details, lists);
          Bazaarboy.post('event/invite/new/', {
            id: eventId,
            message: message,
            details: details,
            lists: lists
          }, function(response) {
            var inviteId;
            if (response.status === 'OK') {
              inviteId = response.invite.pk;
              Bazaarboy.redirect('event/invite/' + inviteId + '/preview');
            }
            scope.saving = false;
          });
        }
      });
    }
  };

  Bazaarboy.event.invite.init();

}).call(this);
