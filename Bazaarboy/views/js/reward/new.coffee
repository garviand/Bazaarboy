Bazaarboy.reward.new =
  attachment: undefined
  gif: undefined
  init: () ->
    scope = this
    # GIF SEARCH
    $('input[name=gif_search]').keypress (e) ->
      if e.which == 13
        $('a.gif-search-start').click()
      return
    $('a.gif-search-start').click () ->
      $('a.gif-search-start').html('Searching...')
      searchTerm = $('input[name=gif_search]').val()
      if searchTerm.trim() is ''
        swal 'You Must Type a Search Term'
        $('a.gif-search-start').html('Search')
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
        $('a.gif-search-start').html('Search')
        return
      return
    $('div#gif-modal div.gifs').on 'click', '.gif', () ->
      $('input[name=gif_search]').val('')
      scope.gif = $(this).attr('data-url')
      $('div#gif-modal').foundation('reveal', 'close')
      $('a.attachment-name').attr('href', $(this).attr('data-url'))
      $('a.attachment-name').html('View Attachment')
      $('a.attachment-name').removeClass('hide')
      scope.attachment = undefined
      return
    $('a.create-reward').click () ->
      if $('input[name=name]').val().trim() is ''
        swal 'Name Cannot Be Blank'
        return
      name = $('input[name=name]').val()
      if $('textarea[name=description]').val().trim() is ''
        swal 'Description Cannot Be Blank'
        return
      description = $('textarea[name=description]').val()
      if not $.isNumeric($('input[name=value]').val()) or $('input[name=value]').val() <= 0
        swal 'Value Must Be a Positive Number'
        return
      value = $('input[name=value]').val()
      useGif = false
      if scope.attachment?
        attachmentId = scope.attachment.pk
      else if scope.gif?
        attachmentId = scope.gif
        useGif = true
      else
        swal 'Must Include An Image for the Reward'
        return
      Bazaarboy.post 'rewards/create/', {profile:profileId, name:name, description:description, value:value, attachment:attachmentId, gif:useGif}, (response) ->
        if response.status is 'OK'
          swal
            type: "success"
            title: 'Reward Created'
            text: 'You can now send it to your own attendees, or allow other organizations to share your reward.'
            , () ->
              Bazaarboy.redirect 'rewards/'
              return
        else
          swal response.message
        return
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
        else
          data.submit()
        return
      done: (event, data) ->
        pdfName = data.files[0].name
        response = jQuery.parseJSON data.result
        if response.status is 'OK'
          scope.attachment = response.pdf
          scope.gif = undefined
          $('a.attachment-name').html(pdfName)
          $('a.attachment-name').attr('href', response.url)
          $('a.attachment-name').removeClass('hide')
          $('a.add-attachment').html('Change Attachment')
        else
          swal response.message
          $('a.add-attachment').html('Add Attachment')
        return
    return

Bazaarboy.reward.new.init()