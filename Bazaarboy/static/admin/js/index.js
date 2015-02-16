(function() {
  Bazaarboy.admin.login = {
    searchProfiles: function(value) {
      Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var profiles;
        if (response.status === 'OK') {
          profiles = response.profiles;
          if (profiles.length > 0) {
            return profiles;
          } else {
            return [];
          }
        }
      });
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('.event-filters a.sort-btn').click(function() {
        $('.event-filters a.sort-btn').removeClass('active');
        $(this).addClass('active');
        if ($(this).data('sort') === 'date') {
          tinysort('.event-list>.event', {
            data: $(this).data('sort'),
            order: 'asc'
          });
        } else {
          tinysort('.event-list>.event', {
            data: $(this).data('sort'),
            order: 'desc'
          });
        }
      });
      $('div.login-profile input[name=profile_name]').autocomplete({
        html: true
      }, {
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
        }
      });
      $('body').on('click', '.autocomplete_result, .admin-login', function(event) {
        var id;
        id = $(this).data('id');
        Bazaarboy.get('admin/login/profile/', {
          id: id
        }, function(response) {
          if (response.status === 'OK') {
            Bazaarboy.redirect('index');
          } else {
            alert(response.message);
          }
        });
      });
      $('div.event_export .input_container input[name=event_name]').keyup(function(event) {
        var value;
        value = $('div.event_export .input_container input[name=event_name]').val();
        if (value) {
          _this.searchEvents(value);
        } else {
          $('div.event_export .event_choices').empty();
        }
      });
    }
  };

  Bazaarboy.admin.login.init();

}).call(this);
