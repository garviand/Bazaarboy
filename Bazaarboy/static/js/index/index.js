(function() {
  Bazaarboy.index.index = {
    createEvent: function(profileId) {
      var _this = this;
      Bazaarboy.post('event/create/', {
        profile: profileId
      }, function(response) {
        if (response.status === 'OK') {
          Bazaarboy.redirect('event/' + response.event.pk + '/basics/');
        } else {
          alert(response.message);
        }
      });
    },
    init: function() {
      var scope;
      scope = this;
      $('div.action-btn.create-event').click(function() {
        var profileId;
        profileId = $(this).attr('data-profile-id');
        scope.createEvent(profileId);
      });
    }
  };

  Bazaarboy.index.index.init();

}).call(this);
