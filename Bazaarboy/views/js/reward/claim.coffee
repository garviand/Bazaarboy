Bazaarboy.reward.claim =
  init: () ->
    scope = this
    $('form#claim-form').submit (e) ->
      e.preventDefault()
      params = $('form#claim-form').serializeObject()
      if params.phone.trim() is ''
        params.phone = undefined
      if params.first_name is ''
        swal 'Must Enter A First Name'
        return
      if params.last_name is ''
        swal 'Must Enter A Last Name'
        return
      if params.email is ''
        swal 'Must Enter An Email'
        return
      Bazaarboy.post 'rewards/claim/complete/', params, (response) ->
        if response.status is 'OK'
          console.log response
        else
          console.log response.message
    return

Bazaarboy.reward.claim.init()