Bazaarboy.reward.index =
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
    $('a.send-reward-btn').click () ->
      $('input[name=reward_id]').val($(this).data('id'))
      $('div#send-reward-modal span.reward-name').html($(this).data('name'))
      $('div#send-reward-modal').foundation('reveal', 'open')
      return
    $('input[name=expiration]').pikaday
      format: 'MM/DD/YYYY'
    add_organizer_debounce = jQuery.debounce(1000, false, scope.search_organizers)
    $('input[name=profile_search]').bind('keypress', add_organizer_debounce)
    $('body').on 'click', 'a.add-reward-submit', () ->
      if not $.isNumeric($('input[name=quantity]').val()) or $('input[name=quantity]').val() <= 0
        swal 'Quantity Must Be a Positive Number'
        return
      quantity = Math.floor($('input[name=quantity]').val())
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
              $('form.add-organizer-form div.organizer').remove()
              $('input[name=profile_search]').val('')
              $('input[name=expiration]').val('')
              $('input[name=quantity]').val('')
              return
        return
      return
    return

Bazaarboy.reward.index.init()