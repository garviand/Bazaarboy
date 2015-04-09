(function() {
  Bazaarboy.reward.claim = {
    claiming: false,
    init: function() {
      var scope;
      scope = this;
      $('div.claim-views').slick({
        adaptiveHeight: true,
        arrows: false,
        draggable: false,
        infinite: false,
        swipe: false,
        speed: 150
      });
      $('a.claim-next').click(function() {
        $('div.claim-views').slick('slickNext');
      });
      $('form#claim-form').submit(function(e) {
        var extra_fields, field_missing, field_missing_name, params;
        e.preventDefault();
        if (!scope.claiming) {
          scope.claiming = true;
          $('input.submit-claim').val('...');
          params = $('form#claim-form').serializeObject();
          if (params.phone.trim() === '') {
            params.phone = void 0;
          }
          if (params.first_name === '') {
            swal('Must Enter A First Name');
            $('input.submit-claim').val('Claim!');
            scope.claiming = false;
            return;
          }
          if (params.last_name === '') {
            swal('Must Enter A Last Name');
            $('input.submit-claim').val('Claim!');
            scope.claiming = false;
            return;
          }
          if (params.email === '') {
            swal('Must Enter An Email');
            $('input.submit-claim').val('Claim!');
            scope.claiming = false;
            return;
          }
          field_missing = false;
          extra_fields = {};
          field_missing_name = '';
          $('input.extra-field').each(function() {
            if ($(this).val().trim() === '') {
              field_missing = true;
              field_missing_name = $(this).data('field');
              console.log(field_missing_name);
            }
            extra_fields[$(this).data('field')] = $(this).val();
          });
          if (field_missing) {
            swal(field_missing_name + ' Cannot Be Blank');
            $('input.submit-claim').val('Claim!');
            scope.claiming = false;
            return;
          }
          params.extra_fields = JSON.stringify(extra_fields);
          Bazaarboy.post('rewards/claim/complete/', params, function(response) {
            scope.claiming = false;
            $('input.submit-claim').val('Claim!');
            if (response.status === 'OK') {
              $('div.claim-views').css('display', 'none');
              return $('div.claim-success').removeClass('hide');
            } else {
              return swal(response.message);
            }
          });
        }
      });
    }
  };

  Bazaarboy.reward.claim.init();

}).call(this);
