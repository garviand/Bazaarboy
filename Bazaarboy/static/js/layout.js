(function() {
  this.Bazaarboy = {
    index: {},
    user: {},
    profile: {},
    event: {},
    admin: {},
    collapseStates: [],
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
    switchCollapsedStates: function(cb) {
      var animations, attr, collapse, collapseAnimations, element, _i, _j, _len, _len1, _ref, _ref1, _to,
        _this = this;
      collapse = !$('body').hasClass('collapsed');
      _to = collapse ? 2 : 1;
      collapseAnimations = [];
      _ref = this.collapseStates;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        element = _ref[_i];
        animations = {};
        _ref1 = element[1];
        for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
          attr = _ref1[_j];
          animations[attr[0]] = attr[_to];
        }
        collapseAnimations.push($(element[0]).stop().animate(animations, 300, 'easeInOutQuint').promise());
      }
      $.when.apply($, collapseAnimations).done(function() {
        if (collapse) {
          $('body').addClass('collapsed');
        } else {
          $('body').removeClass('collapsed');
        }
        return typeof cb === "function" ? cb() : void 0;
      });
    },
    init: function() {
      var _this = this;
      this.collapseStates = [['div#wrapper_top div.logo', [['width', '186px', '60px']]], ['div#wrapper_top div.search', [['width', '750px', '876px']]], ['div#wrapper_sidebar', [['width', '186px', '60px']]], ['div#wrapper_content', [['width', '750px', '876px']]]];
      $('div#wrapper_sidebar div.switch a').click(function() {
        return _this.switchCollapsedStates();
      });
    }
  };

  Bazaarboy.init();

}).call(this);
