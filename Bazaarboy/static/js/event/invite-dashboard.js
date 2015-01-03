(function() {
  Bazaarboy.event.invite_dashboard = {
    sending: false,
    init: function() {
      var scope;
      scope = this;
      $('div.invitation a.delete-invite').click(function() {
        var invitation, inviteId;
        invitation = $(this).closest('div.invitation');
        inviteId = $(this).data('id');
        return swal({
          title: "Are You Sure?",
          text: "Are you sure you want to delete this invitation draft?",
          type: "warning",
          showCancelButton: true,
          confirmButtonText: "Yes",
          closeOnConfirm: true
        }, function() {
          Bazaarboy.post('event/invite/delete/', {
            id: inviteId
          }, function(response) {
            if (response.status === 'OK') {
              invitation.remove();
            } else {
              console.log(response);
            }
          });
        });
      });
    }
  };

  Bazaarboy.event.invite_dashboard.init();

}).call(this);
