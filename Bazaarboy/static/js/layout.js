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
      if (params == null) {
        params = {};
      }
      params.csrfmiddlewaretoken = csrfToken;
      $.get(rootUrl + endpoint, params, function(data) {
        var response;
        response = $.parseJSON(data);
        return typeof cb === "function" ? cb(response) : void 0;
      });
    },
    post: function(endpoint, params, cb) {
      if (params == null) {
        params = {};
      }
      params.csrfmiddlewaretoken = csrfToken;
      $.post(rootUrl + endpoint, params, function(data) {
        var response;
        response = $.parseJSON(data);
        return typeof cb === "function" ? cb(response) : void 0;
      });
    },
    adjustBottomPosition: function() {
      var bottomHeight, contentHeight, topHeight, windowHeight;
      windowHeight = $(window).height();
      topHeight = $('div#wrapper_top').outerHeight();
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
    init: function() {
      var _this = this;
      this.post('timezone/', {
        timezone: getTimezoneName()
      });
      $(document).ready(function() {
        _this.adjustBottomPosition();
      });
      $(window).resize(function() {
        _this.adjustBottomPosition();
      });
    }
  };

  Bazaarboy.init();

}).call(this);
