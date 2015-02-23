Bazaarboy.reward.manage =
  init: () ->
    scope = this
    # SEARCH
    $('input[name=reward_name], input[name=reward_email], input[name=reward_code]').keyup () ->
      searchType = $(this).data('type')
      $('input[data-type!=' + searchType + ']').val('')
      searchVal = $(this).val().toLowerCase()
      console.log(searchType, searchVal)
      if searchVal.trim() isnt ''
        $('div.rewards div.reward').addClass('hide')
        $('div.rewards div.reward[data-'+searchType+'*="'+ searchVal + '"]').removeClass('hide')
      else
        $('div.rewards div.reward').removeClass('hide')
      return
    # REDEEM
    $('div.reward div.redeem a').click () ->
      button = $(this)
      button.html 'Redeeming'
      claimId = $(this).closest('div.reward').data('id')
      Bazaarboy.post 'rewards/redeem/', {claim_id:claimId}, (response) ->
          if response.status is 'OK'
              swal
                  type: 'success'
                  title: 'Reward Redeemed!'
                  text: 'The reward has been redeemed. It is not longer valid.'
              button.html 'Redeemed'
              button.removeClass('secondary-btn')
              button.addClass('disabled-btn')
          else
              swal response.message
              button.html 'Redeem'
        return
      return
    return

Bazaarboy.reward.manage.init()