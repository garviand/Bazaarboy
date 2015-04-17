Bazaarboy.reward.request =
  isSubmitting: false
  attachment: undefined
  gif: undefined
  init: () ->
    scope = this
    # CHOOSE REQUEST TYPE
    $('div.choose-type a.choose-type-btn').click () ->
      $('div.choose-type a.choose-type-btn').addClass('primary-btn-inverse')
      $('div.choose-type a.choose-type-btn').removeClass('primary-btn')
      $('div.choose-type a.choose-type-btn').removeClass('active')
      $(this).removeClass('primary-btn-inverse')
      $(this).addClass('primary-btn')
      $(this).addClass('active')
      if $(this).data('type') == 'message'
        $('div.reward-template').addClass('hide')
      else
        $('div.reward-template').removeClass('hide')
      $('html, body').animate
        scrollTop: $("div.reward-message").offset().top
        , 500
      return
    # REMOVE IMAGE
    $('a.remove-image-btn').click () ->
      scope.attachment = undefined
      scope.gif = undefined
      $('div.listing-image-container').addClass 'hide'
      $('div.listing-image-input-container').removeClass 'hide'
      return
    # GIF SEARCH
    $('input[name=gif_search]').keypress (e) ->
      if e.which == 13
        $('a.gif-search-start').click()
      return
    $('a.gif-search-start').click () ->
      swal
        title: 'Search For Gif'
        html: '<input type="text" name="gif_search" placeholder="GIF Search (pizza, coffee, etc)" />'
        showCancelButton: true
        closeOnConfirm: true
        confirmButtonText: 'Search'
        , () ->
          $('a.gif-search-start').html('Searching...')
          searchTerm = $('input[name=gif_search]').val()
          if searchTerm.trim() is ''
            swal 'You Must Type a Search Term'
            $('a.gif-search-start').html('Search with GIPHY')
            return
          Bazaarboy.get 'rewards/search/gif/', {q:searchTerm}, (response) ->
            response = jQuery.parseJSON response['gifs']
            $('div#gif-modal div.gifs .gif-column').empty()
            count = 0
            gifLength = Math.floor(response.length/3)
            for gif in response
              count += 1
              col = Math.ceil(count/gifLength)
              newGif = $('div#gif-modal .gif-template').clone()
              newGif.find('img').attr 'src', gif.fixed_width.url
              newGif.attr 'data-url', gif.original.url
              newGif.removeClass 'gif-template'
              newGif.removeClass 'hide'
              $('div#gif-modal div.gifs .gifs-' + col).append(newGif)
            $('div#gif-modal').foundation('reveal', 'open')
            $('a.gif-search-start').html('Search with GIPHY')
            return
          return
      return
    $('div#gif-modal div.gifs').on 'click', '.gif', () ->
      $('input[name=gif_search]').val('')
      scope.gif = $(this).attr('data-url')
      $('div#gif-modal').foundation('reveal', 'close')
      $('div.listing-image-container img').attr('src', $(this).attr('data-url'))
      $('div.listing-image-input-container').addClass 'hide'
      $('div.listing-image-container').removeClass 'hide'
      scope.attachment = undefined
      return
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
    $('a.add-attachment').click () ->
      $('input[name=attachment_file]').click()
      return
    $('input[name=attachment_file]').fileupload
      url: rootUrl + 'event/followup/attachment/'
      type: 'POST'
      add: (event, data) ->
        $('a.add-attachment').html('loading...')
        csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val()
        data.formData = {name:data.files[0].name, csrfmiddlewaretoken: csrfmiddlewaretoken}
        if data.files[0].type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
          swal 'Must Be A PNG, JPG or GIF'
          $('a.add-attachment').html('Upload Image')
        else
          data.submit()
        return
      done: (event, data) ->
        pdfName = data.files[0].name
        response = jQuery.parseJSON data.result
        if response.status is 'OK'
          scope.attachment = response.pdf
          scope.gif = undefined
          $('div.listing-image-container img').attr('src', response.url)
          $('div.listing-image-input-container').addClass 'hide'
          $('div.listing-image-container').removeClass 'hide'
          $('a.add-attachment').html('Upload Image')
        else
          swal response.message
          $('a.add-attachment').html('Upload Image')
        return
    # CREATE REQUEST
    $('a.create-request').click () ->
      if not scope.isSubmitting
        button = $(this)
        button.html('Submitting...')
        scope.isSubmitting = true
        params = $('form#request-reward-form').serializeObject()
        if $('div.choose-type a.choose-type-btn.active').length == 0
          swal 'You must select a request type (Message or Template).'
          button.html('Send Request')
          scope.isSubmitting = false
          return
        if params.message.trim() == ''
          swal 'The message cannot be empty'
          button.html('Send Request')
          scope.isSubmitting = false
          return
        if params.event_url.trim() == ''
          params.event_url = undefined
        if  $('div.choose-type a.choose-type-btn.active').data('type') == 'message'
          params.template = false
        else if  $('div.choose-type a.choose-type-btn.active').data('type') == 'template'
          params.template = true
          params.gif = false
          if scope.attachment?
            params.attachment = scope.attachment.pk
          else if scope.gif?
            params.attachment = scope.gif
            params.gif = true
          else
            params.attachment = undefined
          if $('input[name=value]').val().trim() == ''
            params.value = undefined
          else if not $.isNumeric($('input[name=value]').val()) or $('input[name=value]').val() <= 0
            swal 'Item Value Must Be a Positive Number'
            button.html('Send Request')
            scope.isSubmitting = false
        params.sender = profileId
        console.log params
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