Bazaarboy.reward.index =
  sendingGift: false
  search_organizers: () ->
    value = $('input[name=profile_search]').val()
    $('form.add-organizer-form div.organizer').remove()
    organizerModel = $('div.organizer-model')
    Bazaarboy.get 'profile/search/', {keyword: value}, (response) =>
      if response.status is 'OK'
        profiles = response.profiles
        if profiles.length > 0
          for i in [0..profiles.length-1]
            newProfile = organizerModel
            newProfile.find('div.organizer-name').html(profiles[i].name)
            if profiles[i].image_url?
              newProfile.find('div.organizer-image').html('<img src='+profiles[i].image_url+' />')
            else
              newProfile.find('div.organizer-image').html('&nbsp;')
            newProfile.find('a.add-reward-submit').attr('data-profile', profiles[i].pk)
            $('form.add-organizer-form').append(newProfile.html())
  init: () ->
    scope = this
    if totalSent > 9 or hasSubscription
      $('span.free_gifts').addClass('hide')
    # SUBSCRIPTION
    $('a.cancel-subscription').click () ->
      $('div#add-subscription-modal').foundation('reveal', 'close')
      return
    $('div#add-subscription-modal a.create-subscription').click () ->
      StripeCheckout.open
        key: publishableKey
        address: false
        amount: 0
        currency: 'usd'
        name: 'Bazaarboy Gifts Account'
        description: 'Create Account'
        panelLabel: 'Subscribe'
        closed: () ->
          $('div#add-subscription-modal').foundation('reveal', 'close')
          return
        token: (token) =>
          Bazaarboy.post 'rewards/subscribe/',
            stripe_token: token.id
            email: token.email
            profile: profileId
          , (response) =>
            if response.status is 'OK'
              swal
                type: "success"
                title: 'Subscribed!'
                text: 'You have successfully subscribed for a Bazaarboy account!'
                , () ->
                  location.reload()
                  return
            else
              alert response.message
            return
          return
      return
    # DISTRIBUTE REWARD
    $('div.reward a.send-gift-item').click () ->
      rewardItemId = $(this).data('id')
      rewardItemName = $(this).data('name')
      $('div#distribute-reward-modal input[name=reward_item_id]').val(rewardItemId)
      $('div#distribute-reward-modal span.reward-name').html(rewardItemName)
      $('div#distribute-reward-modal').foundation('reveal', 'open')
      return
    $('div#distribute-reward-modal a.send-gift-btn').click () ->
      if not scope.sendingGift
        button = $(this)
        button.html('Sending...')
        scope.sendingGift = true
        rewardEmail = $('div#distribute-reward-modal input[name=email_distribute]').val()
        rewardMessage = $('div#distribute-reward-modal textarea[name=email_message]').val()
        rewardItem = $('div#distribute-reward-modal input[name=reward_item_id]').val()
        if rewardEmail.trim() is ''
          swal 'Must Enter an Email'
          scope.sendingGift = false
          return
        Bazaarboy.post 'rewards/claim/add/', {item:rewardItem, email:rewardEmail, message:rewardMessage}, (response) ->
          if response.status is 'OK'
              swal
                  type: 'success'
                  title: 'Gift Sent'
                  text: 'The gift has been sent.'
              $('div#distribute-reward-modal').foundation('reveal', 'close')
              button.html 'Send Gift'
              scope.sendingGift = false
              $('div.rewards div.reward[data-id=' + rewardItem + '] span.quantity').html(response.reward_item.quantity)
              $('div#distribute-reward-modal input[name=email_distribute]').val('')
          else
              swal response.message
              button.html 'Send Gift'
              scope.sendingGift = false
          return
      return
    # SEND REWARD
    $('div#send-reward-modal a.add-reward-profile').click () ->
      $('div#send-reward-modal div.profile-search').removeClass 'hide'
      $('div#send-reward-modal div.email-send').addClass 'hide'
      $(this).addClass('primary-btn')
      $(this).removeClass('primary-btn-inverse')
      $('div#send-reward-modal a.add-reward-email').removeClass('primary-btn')
      $('div#send-reward-modal a.add-reward-email').addClass('primary-btn-inverse')
      return
    $('div#send-reward-modal a.add-reward-email').click () ->
      $('div#send-reward-modal form.add-organizer-form').empty()
      $('div#send-reward-modal div.email-send').removeClass 'hide'
      $('div#send-reward-modal div.profile-search').addClass 'hide'
      $(this).addClass('primary-btn')
      $(this).removeClass('primary-btn-inverse')
      $('div#send-reward-modal a.add-reward-profile').removeClass('primary-btn')
      $('div#send-reward-modal a.add-reward-profile').addClass('primary-btn-inverse')
      return
    $('body').on 'click', 'a.send-reward-btn', () ->
      if totalSent > 9 and not hasSubscription
        $('div#add-subscription-modal').foundation('reveal', 'open')
      else
        $('input[name=reward_id]').val($(this).data('id'))
        $('div#send-reward-modal span.reward-name').html($(this).data('name'))
        $('div#send-reward-modal').foundation('reveal', 'open')
      return
    $('input[name=expiration]').pikaday
      format: 'MM/DD/YYYY'
    add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers)
    $('input[name=profile_search]').bind('keypress', add_organizer_debounce)
    # SEND TO EMAIL
    $('div#send-reward-modal a.send-via-email').click () ->
      if not $.isNumeric($('input[name=quantity]').val()) or $('input[name=quantity]').val() <= 0
        swal 'Quantity Must Be a Positive Number'
        return
      quantity = Math.floor($('input[name=quantity]').val())
      if (10 - totalSent) < quantity and not hasSubscription
        swal
          type: "warning"
          title: "Trial Exceeded"
          text: "You do not have enough free gifts left to send this much inventory. Subscribe to a Bazaarboy account now?"
          showCancelButton: true
          confirmButtonText: 'Subscribe'
          cancelButtonText: 'Cancel'
          , (isConfirm) ->
            if isConfirm
              $('div#add-subscription-modal').foundation('reveal', 'open')
            return
        return
      expiration = $('input[name=expiration]').val()
      if not moment(expiration, 'MM/DD/YYYY').isValid()
        swal 'Expiration Date is Not Valid'
        return
      expirationTime = moment(expiration, 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss')
      rewardId = $('input[name=reward_id]').val()
      email = $('div#send-reward-modal input[name=email_send]').val()
      if email.trim() is ''
        swal 'Must Enter An Email'
        return
      Bazaarboy.post 'rewards/item/add/', {reward:rewardId, email:email, quantity:quantity, expiration_time:expirationTime}, (response) ->
        if response.status is 'OK'
          swal
            type: "success"
            title: 'Reward Sent'
            text: 'You sent ' + response.reward_send.quantity + ' \'' + response.reward_send.reward.name + '\' rewards to ' + response.reward_send.email 
            , () ->
              location.reload()
              return
      return
    # SEND TO ACCOUNT
    $('body').on 'click', 'a.add-reward-submit', () ->
      if not $.isNumeric($('input[name=quantity]').val()) or $('input[name=quantity]').val() <= 0
        swal 'Quantity Must Be a Positive Number'
        return
      quantity = Math.floor($('input[name=quantity]').val())
      if (10 - totalSent) < quantity and not hasSubscription
        swal
          type: "warning"
          title: "Trial Exceeded"
          text: "You do not have enough free gifts left to send this much inventory. Subscribe to a Bazaarboy account now?"
          showCancelButton: true
          confirmButtonText: 'Subscribe'
          cancelButtonText: 'Cancel'
          , (isConfirm) ->
            if isConfirm
              $('div#add-subscription-modal').foundation('reveal', 'open')
            return
        return
      expiration = $('input[name=expiration]').val()
      if not moment(expiration, 'MM/DD/YYYY').isValid()
        swal 'Expiration Date is Not Valid'
        return
      expirationTime = moment(expiration, 'MM/DD/YYYY').utc().format('YYYY-MM-DD HH:mm:ss')
      rewardId = $('input[name=reward_id]').val()
      profileId = $(this).data('profile')
      Bazaarboy.post 'rewards/item/add/', {reward:rewardId, owner:profileId, quantity:quantity, expiration_time:expirationTime}, (response) ->
        if response.status is 'OK'
          swal
            type: "success"
            title: 'Reward Sent'
            text: 'You sent ' + response.reward_item.quantity + ' \'' + response.reward_item.reward.name + '\' rewards to ' + response.reward_item.owner.name 
            , () ->
              location.reload()
              return
        return
      return
    return

Bazaarboy.reward.index.init()