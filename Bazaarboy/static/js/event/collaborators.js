(function() {
  Bazaarboy.event.collaborators = {
    sending: false,
    search_organizers: function() {
      var organizerModel, value,
        _this = this;
      $('form.add-organizer-form div.organizer').remove();
      organizerModel = $('div.organizer-model');
      value = $('form.add-organizer-form input#organizer-name').val();
      Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var i, newProfile, profiles, _i, _ref;
        if (response.status === 'OK') {
          profiles = response.profiles;
          if (profiles.length > 0) {
            $('.profile_login .profile_choices').empty();
            for (i = _i = 0, _ref = profiles.length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
              newProfile = organizerModel;
              newProfile.find('div.organizer-name').html(profiles[i].name);
              if (profiles[i].image_url != null) {
                newProfile.find('div.organizer-image').html('<img src=' + profiles[i].image_url + ' />');
              } else {
                newProfile.find('div.organizer-image').html('&nbsp;');
              }
              newProfile.find('a.add-organizer-submit').attr('data-profile', profiles[i].pk);
              $('form.add-organizer-form').append(newProfile.html());
            }
          }
        }
      });
    },
    init: function() {
      var add_organizer_debounce, scope;
      scope = this;
      $('a.add-organizer-btn').click(function() {
        $('div#add-organizer-modal').foundation('reveal', 'open');
      });
      $('a.add-organizer-close').click(function() {
        $('div#add-organizer-modal').foundation('reveal', 'close');
      });
      $('a.add-organizer-another').click(function() {
        $('div.row.add-organizer-success').fadeOut(300, function() {
          $('form.add-organizer-form').fadeIn(300);
        });
      });
      add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers);
      $('form.add-organizer-form input#organizer-name').bind('keypress', add_organizer_debounce);
      $('form.add-organizer-form').on('click', 'a.add-organizer-submit', function() {
        var profileId,
          _this = this;
        profileId = $(this).data('profile');
        Bazaarboy.post('event/organizer/request/', {
          id: eventId,
          profile: profileId
        }, function(response) {
          if (response.status === 'OK') {
            $('form.add-organizer-form').fadeOut(300, function() {
              var newReq;
              $('form.add-organizer-form input#organizer-name').val('');
              $('form.add-organizer-form div.organizer').remove();
              $('div.row.add-organizer-success').fadeIn(300);
              newReq = $('div.request_template').clone();
              newReq.find('div.request_name').html(response.collaboration.profile.name);
              newReq.removeClass('request_template');
              newReq.removeClass('hide');
              $('div.pending').append(newReq);
              $('div.pending').removeClass('hide');
            });
          } else {
            swal(response.message);
          }
        });
      });
      $('form.add-organizer-form a.send-request-btn').click(function() {
        var email,
          _this = this;
        email = $('form.add-organizer-form input[name=organizer_email]').val();
        if (email.trim() !== '') {
          Bazaarboy.post('event/organizer/request/', {
            id: eventId,
            email: email
          }, function(response) {
            if (response.status === 'OK') {
              $('form.add-organizer-form').fadeOut(300, function() {
                var newReq;
                $('form.add-organizer-form input#organizer-name').val('');
                $('form.add-organizer-form div.organizer').remove();
                $('div.row.add-organizer-success').fadeIn(300);
                newReq = $('div.request_template').clone();
                newReq.find('div.request_name').html(response.collaboration.email);
                newReq.removeClass('request_template');
                newReq.removeClass('hide');
                $('div.pending').append(newReq);
                $('div.pending').removeClass('hide');
              });
            } else {
              swal(response.message);
            }
          });
        }
      });
    }
  };

  Bazaarboy.event.collaborators.init();

}).call(this);
