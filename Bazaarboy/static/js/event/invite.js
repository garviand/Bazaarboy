(function() {
  Bazaarboy.event.invite = {
    init: function() {
      var typewatch_options;
      typewatch_options = {
        callback: function(value) {
          $(".template_container #organizer_message").html($("form.email_form textarea[name=message]").val());
        },
        wait: 750,
        highlight: true
      };
      $("form.email_form textarea[name=message]").typeWatch(typewatch_options);
      $('input[name=include_cover]').change(function() {
        if ($(this).is(':checked')) {
          $(".template_container #cover_image").show();
        } else {
          $(".template_container #cover_image").hide();
        }
      });
    }
  };

  Bazaarboy.event.invite.init();

}).call(this);
