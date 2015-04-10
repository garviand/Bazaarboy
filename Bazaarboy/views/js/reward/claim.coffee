Bazaarboy.reward.claim =
  claiming:false
  init: () ->
    scope = this
    $('div.claim-views').slick
      adaptiveHeight: true
      arrows: false
      draggable: false
      infinite: false
      swipe: false
      speed: 150
      accessibility: false
    $('a.claim-next').click () ->
      $('div.claim-views').slick('slickNext')
      return
    $('form#claim-form').submit (e) ->
      e.preventDefault()
      if not scope.claiming
        scope.claiming = true
        $('input.submit-claim').val('...')
        params = $('form#claim-form').serializeObject()
        if params.phone.trim() is ''
          params.phone = undefined
        if params.first_name is ''
          swal 'Must Enter A First Name'
          $('input.submit-claim').val('Claim!')
          scope.claiming = false
          return
        if params.last_name is ''
          swal 'Must Enter A Last Name'
          $('input.submit-claim').val('Claim!')
          scope.claiming = false
          return
        if params.email is ''
          swal 'Must Enter An Email'
          $('input.submit-claim').val('Claim!')
          scope.claiming = false
          return
        field_missing = false
        extra_fields = {}
        field_missing_name = ''
        $('input.extra-field').each () ->
          if $(this).val().trim() is ''
            field_missing = true
            field_missing_name = $(this).data('field')
            console.log field_missing_name
          extra_fields[$(this).data('field')] = $(this).val()
          return
        if field_missing
          swal field_missing_name + ' Cannot Be Blank'
          $('input.submit-claim').val('Claim!')
          scope.claiming = false
          return
        params.extra_fields = JSON.stringify(extra_fields)
        if isGiveaway
          targetUrl = 'rewards/giveaway/complete/'
        else
          targetUrl = 'rewards/claim/complete/'
        Bazaarboy.post targetUrl, params, (response) ->
          scope.claiming = false
          $('input.submit-claim').val('Claim!')
          if response.status is 'OK'
            $('div.claim-views').css('display', 'none')
            $('div.claim-success').removeClass('hide')
          else
            swal response.message
      return
    return

Bazaarboy.reward.claim.init()