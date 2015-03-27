Bazaarboy.reward.redeem =
  redeeming:false
  init: () ->
    scope = this
    $('form#redeem-form').submit (e) ->
      e.preventDefault()
      if not scope.redeeming
        scope.redeeming = true
        Bazaarboy.post 'rewards/redeem/', {claim_id:claim_id, token:claim_token}, (response) ->
          if response.status is 'OK'
            $('div.redemption-info').addClass 'hide'
            $('div.redemption-success').removeClass 'hide'
            swal
              type: 'success'
              title: 'Redeemed!'
              text: 'The gift has been redeemed.'
          else
            swal
              type: 'warning'
              title: 'Oops'
              text: response.message
          return
    return

Bazaarboy.reward.redeem.init()