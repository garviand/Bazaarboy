(function() {
  this.Bazaarboy = {
    index: {},
    user: {},
    profile: {},
    event: {},
    admin: {},
    redirect: function(endpoint) {
      var redirectUrl;
      redirectUrl = rootUrl;
      if (endpoint !== 'index') {
        redirectUrl = rootUrl + endpoint;
      }
      window.location.href = redirectUrl;
    },
    get: function(endpoint, params, cb) {
      var promise;
      if (params == null) {
        params = {};
      }
      params.csrfmiddlewaretoken = csrfToken;
      promise = $.get(rootUrl + endpoint, params, function(data) {
        var response;
        response = $.parseJSON(data);
        return typeof cb === "function" ? cb(response) : void 0;
      });
      return promise;
    },
    post: function(endpoint, params, cb) {
      var promise;
      if (params == null) {
        params = {};
      }
      params.csrfmiddlewaretoken = csrfToken;
      promise = $.post(rootUrl + endpoint, params, function(data) {
        var response;
        response = $.parseJSON(data);
        return typeof cb === "function" ? cb(response) : void 0;
      });
      return promise;
    },
    adjustBottomPosition: function() {
      var bottomHeight, contentHeight, topHeight, windowHeight;
      windowHeight = $(window).height();
      topHeight = $('div#wrapper_top').outerHeight();
      if ($('div#wrapper_top').hasClass('hidden')) {
        topHeight = 0;
      }
      contentHeight = $('div#wrapper_content').outerHeight();
      bottomHeight = $('div#wrapper_bottom').outerHeight();
      if (windowHeight - bottomHeight > topHeight + contentHeight) {
        $('div#wrapper_bottom').css({
          'position': 'fixed',
          'bottom': 0
        });
      } else {
        $('div#wrapper_bottom').css({
          'position': '',
          'bottom': ''
        });
      }
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
    init: function() {
      var scope,
        _this = this;
      scope = this;
      this.post('timezone/', {
        timezone: getTimezoneName()
      });
      $(document).ready(function() {
        _this.adjustBottomPosition();
      });
      $(window).resize(function() {
        _this.adjustBottomPosition();
      });
      $('#wrapper_top .controls .user_create_event a').click(function(e) {
        var profileId;
        e.preventDefault();
        profileId = $(this).data('id');
        scope.createEvent(profileId);
      });
    }
  };

  Bazaarboy.init();

}).call(this);
