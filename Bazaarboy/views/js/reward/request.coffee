Bazaarboy.reward.request =
  isSubmitting: false
  init: () ->
    scope = this
    # SEARCH PROFILES
    $('input[name=search_name]').autocomplete
      html: true,
      source: (request, response) ->
        Bazaarboy.get 'profile/search/', {keyword: request.term}, (results) ->
          profiles = []
          for profile in results.profiles
            thisLabel = '<div class="autocomplete_result row" data-id="' + profile.pk + '">'
            if profile.image_url?
              thisLabel += '<div class="small-1 columns autocomplete_image" style="background-image:url(' + profile.image_url + '); background-size:contain; background-position:center; background-repeat:no-repeat;" />'
            thisLabel += '<div class="small-11 columns autocomplete_name">' + profile.name + '</div>'
            thisLabel += '</div>'
            profiles.push({label: thisLabel, value: profile.name})
          return response(profiles)
        return
      select: (event, ui) ->
        requestProfile = $(event.currentTarget).find('.autocomplete_result').data('id')
        $('input[name=profile]').val(requestProfile)
        return
    # CREATE REQUEST
    $('a.create-request').click () ->
      if not scope.isSubmitting
        button = $(this)
        button.html('Submitting...')
        scope.isSubmitting = true
        params = $('form#request-reward-form').serializeObject()
        if params.message.trim() == ''
          swal 'The message cannot be empty'
          button.html('Send Request')
          scope.isSubmitting = false
          return
        if params.event_url.trim() == ''
          params.event_url = undefined
        Bazaarboy.post 'rewards/request/create/', params, (response) ->
          if response.status is 'OK'
            swal
              type:'success'
              title:'Request Sent'
              text:'Your gift request has been sent. You will be notified with the reply!'
              , () ->
                Bazaarboy.redirect 'rewards/'
                return
          else
            swal
              type:'warning'
              title:'Hold On!'
              text: response.message
              , () ->
                scope.isSubmitting = false
                button.html('Send Request')
                return
      return
    return

Bazaarboy.reward.request.init()