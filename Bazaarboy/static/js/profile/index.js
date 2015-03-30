(function() {
  Bazaarboy.profile.index = {
    init: function() {
      var scope;
      scope = this;
      $('div.past-events-slider').slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        responsive: [
          {
            breakpoint: 480,
            settings: {
              slidesToShow: 1,
              slidesToScroll: 1
            }
          }
        ]
      });
    }
  };

  Bazaarboy.profile.index.init();

}).call(this);
