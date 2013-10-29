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
    init: function() {
      this.post('timezone/', {
        timezone: getTimezoneName()
      });
    }
  };

  Bazaarboy.init();

}).call(this);
