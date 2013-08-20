(function() {
  this.Bazaarboy = {
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
        if (cb != null) {
          return cb(response);
        }
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
        if (cb != null) {
          return cb(response);
        }
      });
    },
    index: {},
    user: {},
    profile: {},
    event: {},
    admin: {},
    collapseStates: {},
    init: function() {
      var _this = this;
      this.collapseStates = [['div#wrapper_top div.logo', [['width', '186px', '60px']]], ['div#wrapper_top div.search', [['width', '750px', '876px']]], ['div#wrapper_sidebar', [['width', '186px', '60px']]], ['div#wrapper_content', [['width', '750px', '876px']]]];
      $('div#wrapper_sidebar div.switch a').click(function() {
        var collapse, collapseAnimations, _to;
        collapse = !$('body').hasClass('collapsed');
        _to = collapse ? 2 : 1;
        collapseAnimations = $.map(_this.collapseStates, function(element, i) {
          var animations, attr, _i, _len, _ref;
          animations = {};
          _ref = element[1];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            attr = _ref[_i];
            animations[attr[0]] = attr[_to];
          }
          return $(element[0]).stop().animate(animations, 300, 'easeInOutQuint').promise();
        });
        $.when(collapseAnimations).then(function() {
          if (collapse) {
            $('body').addClass('collapsed');
          } else {
            $('body').removeClass('collapsed');
          }
        });
      });
    }
  };

  Bazaarboy.init();

}).call(this);
