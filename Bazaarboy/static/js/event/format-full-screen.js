(function() {
  Bazaarboy.event.format_full_screen = {
    ticketMenu: void 0,
    ticketId: void 0,
    DropDown: function(el) {
      this.dd = el;
      this.placeholder = this.dd.children('span');
      this.opts = this.dd.find('ul.dropdown > li');
      this.val = '';
      this.index = -1;
      this.ticket = void 0;
      return this.initEvents();
    },
    init: function() {
      var scope;
      scope = this;
      if ($('.tix-type').length === 1) {
        scope.ticketId = $('.tix-type').data('id');
      }
      this.DropDown.prototype = {
        initEvents: function() {
          var obj;
          obj = this;
          obj.dd.on("click", function(event) {
            $(this).toggleClass("active");
            false;
          });
          obj.opts.on("click", function() {
            var opt;
            opt = $(this);
            obj.val = opt.text();
            obj.index = opt.index();
            obj.placeholder.text(obj.val);
            scope.ticketId = opt.find('a').data('id');
          });
        },
        getValue: function() {
          this.val;
        },
        getIndex: function() {
          this.index;
        }
      };
      this.ticketMenu = new this.DropDown($('#dd'));
      $("form.hero-ticket-form button[type=submit], .tix-type").click(function(e) {
        var ticketId,
          _this = this;
        e.preventDefault();
        ticketId = scope.ticketId;
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
