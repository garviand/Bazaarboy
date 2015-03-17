(function() {
  this.Bazaarboy.landing = {
    searchEvents: function(value) {
      return Bazaarboy.get('profile/search/', {
        keyword: value
      }, function(response) {
        var profiles;
        if (response.status === 'OK') {
          profiles = response.profiles;
          if (profiles.length > 0) {
            return profiles;
          } else {
            return [];
          }
        }
      });
    },
    init: function() {
      $('input[name=event_name]').autocomplete({
        html: true,
        source: function(request, response) {
          Bazaarboy.get('event/search/', {
            keyword: request.term
          }, function(results) {
            var events, evnt, thisLabel, _i, _len, _ref;
            events = [];
            _ref = results.events;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              evnt = _ref[_i];
              thisLabel = '<div class="autocomplete_result row" data-id="' + evnt.pk + '">';
              if (evnt.image_url != null) {
                thisLabel += '<div class="small-2 columns autocomplete_image" style="background-image:url(' + evnt.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;" />';
              }
              thisLabel += '<div class="small-10 columns autocomplete_name">' + evnt.name + '</div>';
              thisLabel += '</div>';
              events.push({
                label: thisLabel,
                value: evnt.name
              });
            }
            return response(events);
          });
        }
      });
      $('div.slider-container div.organizer-slider').slick({
        arrows: false
      });
      $('ul.slider-controls div.logo-container a').click(function() {
        var slideNum;
        slideNum = $(this).closest('div.logo-container').data('slidenum');
        $('div.slider-container div.organizer-slider').slick('slickGoTo', slideNum);
      });
      $('div.slider-container div.organizer-slider').on('afterChange', function(event, slick, currentSlide, nextSlide) {
        $('ul.slider-controls div.logo-container').removeClass('active');
        $('ul.slider-controls div.logo-container[data-slidenum=' + currentSlide + ']').addClass('active');
      });
    }
  };

  Bazaarboy.landing.init();

}).call(this);
