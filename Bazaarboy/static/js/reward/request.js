(function() {
  Bazaarboy.reward.request = {
    isSubmitting: false,
    init: function() {
      var scope;
      scope = this;
      $('input[name=search_name]').autocomplete({
        html: true,
        source: function(request, response) {
          Bazaarboy.get('profile/search/', {
            keyword: request.term
          }, function(results) {
            var profile, profiles, thisLabel, _i, _len, _ref;
            profiles = [];
            _ref = results.profiles;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              profile = _ref[_i];
              thisLabel = '<div class="autocomplete_result row" data-id="' + profile.pk + '">';
              if (profile.image_url != null) {
                thisLabel += '<div class="small-1 columns autocomplete_image" style="background-image:url(' + profile.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;" />';
              }
              thisLabel += '<div class="small-11 columns autocomplete_name">' + profile.name + '</div>';
              thisLabel += '</div>';
              profiles.push({
                label: thisLabel,
                value: profile.name
              });
            }
            return response(profiles);
          });
        },
        select: function(event, ui) {
          var requestProfile;
          requestProfile = $(event.currentTarget).find('.autocomplete_result').data('id');
          $('input[name=profile]').val(requestProfile);
        }
      });
      $('a.create-request').click(function() {
        var button, params;
        if (!scope.isSubmitting) {
          button = $(this);
          button.html('Submitting...');
          scope.isSubmitting = true;
          params = $('form#request-reward-form').serializeObject();
          if (params.message.trim() === '') {
            swal('The message cannot be empty');
            button.html('Send Request');
            scope.isSubmitting = false;
            return;
          }
          if (params.event_url.trim() === '') {
            params.event_url = void 0;
          }
          Bazaarboy.post('rewards/request/create/', params, function(response) {
            if (response.status === 'OK') {
              return swal({
                type: 'success',
                title: 'Request Sent',
                text: 'Your gift request has been sent. You will be notified with the reply!'
              }, function() {
                Bazaarboy.redirect('rewards/');
              });
            } else {
              return swal({
                type: 'warning',
                title: 'Hold On!',
                text: response.message
              }, function() {
                scope.isSubmitting = false;
                button.html('Send Request');
              });
            }
          });
        }
      });
    }
  };

  Bazaarboy.reward.request.init();

}).call(this);
