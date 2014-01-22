(function() {
  Bazaarboy.event.invite = {
    init: function() {
      var options;
      options = {
        callback: function(value) {
          $(".template_container #organizer_message").html($("form.email_form textarea[name=message]").val());
        },
        wait: 750,
        highlight: true
      };
      $("form.email_form textarea[name=message]").typeWatch(options);
    }
  };

  Bazaarboy.event.invite.init();

}).call(this);
