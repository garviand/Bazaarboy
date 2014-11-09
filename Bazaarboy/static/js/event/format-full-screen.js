(function() {
  Bazaarboy.event.format_full_screen = {
    init: function() {
      $("form.hero-ticket-form button[type=submit]").click(function(e) {
        var ticketId,
          _this = this;
        e.preventDefault();
        ticketId = $("form.hero-ticket-form .tix-type").data('id');
        if (!$("div#tickets div.ticket[data-id=" + ticketId + "]").hasClass('active')) {
          $("div#tickets div.ticket[data-id=" + ticketId + "] div.ticket-top").click();
        }
        if (!Bazaarboy.event.index.overlayAnimationInProgress) {
          $("html, body").animate({
            scrollTop: 0
          }, "fast");
          if ($('div#wrapper-overlay').hasClass('hide')) {
            Bazaarboy.event.index.overlayAnimationInProgress = true;
            $('div#wrapper-overlay').css('opacity', 0).removeClass('hide');
            $('div#tickets').css('opacity', 0).removeClass('hide');
            $('div#wrapper-overlay').animate({
              opacity: 1
            }, 300);
            return $('div#tickets').animate({
              opacity: 1
            }, 300, function() {
              Bazaarboy.event.index.overlayAnimationInProgress = false;
            });
          }
        }
      });
    }
  };

  Bazaarboy.event.format_full_screen.init();

}).call(this);
