(function() {
  Bazaarboy.event.follow_up_dashboard = {
    init: function() {
      var scope;
      scope = this;
      $('div.comm a.delete-follow-up').click(function() {
        var follow_up, follow_up_id;
        follow_up = $(this).closest('div.comm');
        follow_up_id = $(this).data('id');
        return swal({
          title: "Are You Sure?",
          text: "Are you sure you want to delete this follow up draft?",
          type: "warning",
          showCancelButton: true,
          confirmButtonText: "Yes",
          closeOnConfirm: true
        }, function() {
          Bazaarboy.post('event/followup/delete/', {
            id: follow_up_id
          }, function(response) {
            if (response.status === 'OK') {
              follow_up.remove();
            } else {
              console.log(response);
            }
          });
        });
      });
    }
  };

  Bazaarboy.event.follow_up_dashboard.init();

}).call(this);
