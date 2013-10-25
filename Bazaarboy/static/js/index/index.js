(function() {
  Bazaarboy.index.index = {
    adjustOverlayHeight: function() {
      var height, i, _i, _ref;
      height = 0;
      for (i = _i = 0, _ref = $('div.overlay_canvas > div').not('div.hidden').length; 0 <= _ref ? _i < _ref : _i > _ref; i = 0 <= _ref ? ++_i : --_i) {
        height += $($('div.overlay_canvas > div').not('div.hidden')[i]).outerHeight(true);
      }
      $('div.overlay_canvas').height(height);
    },
    createEvent: function(profileId) {
      var _this = this;
      Bazaarboy.post('event/create/', {
        profile: profileId
      }, function(response) {
        if (response.status === 'OK') {
          Bazaarboy.redirect('event/' + response.event.pk + '/');
        } else {
          alert(response.message);
        }
      });
    },
    savePaymentConnectSettings: function() {
      var promises;
      promises = [];
      $('div#connect div.profiles form').each(function() {
        var params, promise;
        params = $(this).serializeObject();
        if (parseInt(params.payment) > 0) {
          promise = Bazaarboy.post('profile/edit/', params, function(response) {
            if (response.status !== 'OK') {
              alert(response.message);
            }
          });
          promises.push(promise);
        }
      });
      $.when.apply($, promises).done(function() {
        window.location.href = window.location.href.split('#')[0];
      });
    },
    showPaymentConnectOverlay: function() {
      var _this = this;
      $('div#wrapper_overlay').addClass('show').fadeIn(200);
      $('div#connect').fadeIn(200, function() {
        return _this.adjustOverlayHeight();
      });
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      $('div#index div.profile div.header div.create a').click(function() {
        var profileId;
        profileId = $(this).parent().find('span.profile_id').html();
        scope.createEvent(profileId);
      });
      $('div#index div.profiles div.profile div.summary a.connect').click(function() {
        if ($('div#connect').length === 0) {
          window.location.href = stripeConnectUrl;
        } else {
          _this.showPaymentConnectOverlay();
        }
      });
      $('div#wrapper_overlay').click(function() {
        if (!$(this).hasClass('show')) {
          $('div#wrapper_overlay').fadeOut(200);
          $('div.overlay_canvas').fadeOut(200);
        }
      });
      $('div#connect div.actions a.save').click(function() {
        _this.savePaymentConnectSettings();
      });
      if ((window.location.hash != null) && window.location.hash === '#connect') {
        this.showPaymentConnectOverlay();
      }
    }
  };

  Bazaarboy.index.index.init();

}).call(this);
