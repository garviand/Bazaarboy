Bazaarboy.reward.claim =
  claiming:false
  init: () ->
    scope = this
    $('form#claim-form').submit (e) ->
      if not scope.claiming
        scope.claiming = true
        $('input.submit-claim').val('Claiming...')
        e.preventDefault()
        params = $('form#claim-form').serializeObject()
        if params.phone.trim() is ''
          params.phone = undefined
        if params.first_name is ''
          swal 'Must Enter A First Name'
          $('input.submit-claim').val('Claim Reward!')
          scope.claiming = false
          return
        if params.last_name is ''
          swal 'Must Enter A Last Name'
          $('input.submit-claim').val('Claim Reward!')
          scope.claiming = false
          return
        if params.email is ''
          swal 'Must Enter An Email'
          $('input.submit-claim').val('Claim Reward!')
          scope.claiming = false
          return
        Bazaarboy.post 'rewards/claim/complete/', params, (response) ->
          scope.claiming = false
          $('input.submit-claim').val('Claim Reward!')
          if response.status is 'OK'
            $('div.claim-success b.code').html(response.claim.code)
            $('div.claim-inputs').addClass('hide')
            $('div.claim-success').removeClass('hide')
          else
            swal response.message
      return
    return

Bazaarboy.reward.claim.init()