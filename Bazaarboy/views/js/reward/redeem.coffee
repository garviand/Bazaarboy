Bazaarboy.reward.redeem =
  redeeming:false
  init: () ->
    scope = this
    $('a.redeem-btn').click () ->
      $('form#redeem-form').submit()
      return
    $('form#redeem-form').submit (e) ->
      e.preventDefault()
      if not scope.redeeming
        scope.redeeming = true
        swal
          type: 'warning'
          title: 'You Sure?'
          text: 'DO NOT REDEEM unless you are the gift provider.'
          showCancelButton: true
          confirmButtonText: "Yes, Redeem"
          closeOnConfirm: true
          animation: false
          , ()->
            Bazaarboy.post 'rewards/redeem/', {claim_id:claim_id, token:claim_token}, (response) ->
              if response.status is 'OK'
                $('div.redemption-info').addClass 'hide'
                $('div.redemption-success').removeClass 'hide'
              else
                swal
                  type: 'warning'
                  title: 'Oops'
                  text: response.message
              return
        scope.redeeming = false
    return

Bazaarboy.reward.redeem.init()