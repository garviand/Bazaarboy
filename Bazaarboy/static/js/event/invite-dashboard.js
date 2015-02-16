(function() {
  Bazaarboy.event.invite_dashboard = {
    sending: false,
    init: function() {
      var scope;
      scope = this;
      $('a.create-invite-btn').click(function() {
        if (numLists === 0) {
          return swal({
            title: "Hold On!",
            text: "Before sending an invite, create a list of contacts (ie friends, guests) to notify.",
            type: "warning",
            showCancelButton: true,
            confirmButtonText: "Create List",
            closeOnConfirm: true
          }, function() {
            $("div#new-list-modal").foundation('reveal', 'open');
          });
        }
      });
      $("a.close-list-modal").click(function() {
        $("div#new-list-modal").foundation('reveal', 'close');
      });
      $("div#new-list-modal div.new-list-inputs a.create-list").click(function() {
        var list_name;
        $(this).html('Creating...');
        list_name = $("div#new-list-modal div.new-list-inputs input[name=list_name]").val();
        if (list_name.trim() !== '') {
          Bazaarboy.post('lists/create/', {
            profile: profileId,
            name: list_name,
            is_hidden: 1
          }, function(response) {
            if (response.status === 'OK') {
              Bazaarboy.redirect('lists/' + response.list.pk + '/?eid=' + String(eventId));
            }
          });
        } else {
          swal('List name can\'t be empty');
        }
      });
      $('div.comm a.copy-invite').click(function() {
        var inviteId;
        inviteId = $(this).data('id');
        Bazaarboy.post('event/invite/' + inviteId + '/copy/', {}, function(response) {
          if (response.status === 'OK') {
            Bazaarboy.redirect('event/invite/' + response.invite.pk + '/edit/');
          } else {
            swal(response.message);
          }
        });
      });
      $('div.comm a.delete-invite').click(function() {
        var invitation, inviteId;
        invitation = $(this).closest('div.comm');
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
