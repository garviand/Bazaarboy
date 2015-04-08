Bazaarboy.reward.new =
  attachment: undefined
  gif: undefined
  creating: false
  init: () ->
    scope = this
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
    $('a.create-reward').click () ->
      if not scope.creating
        scope.creating = true
        $('a.create-reward').html('Creating...')
        if $('input[name=name]').val().trim() is ''
          swal 'Name Cannot Be Blank'
          $('a.create-reward').html('Create Inventory Item')
          scope.creating = false
          return
        name = $('input[name=name]').val()
        if $('textarea[name=description]').val().trim() is ''
          swal 'Description Cannot Be Blank'
          $('a.create-reward').html('Create Inventory Item')
          scope.creating = false
          return
        description = $('textarea[name=description]').val()
        if not $.isNumeric($('input[name=value]').val()) or $('input[name=value]').val() <= 0
          swal 'Value Must Be a Positive Number'
          $('a.create-reward').html('Create Inventory Item')
          scope.creating = false
          return
        value = $('input[name=value]').val()
        useGif = false
        if scope.attachment?
          attachmentId = scope.attachment.pk
        else if scope.gif?
          attachmentId = scope.gif
          useGif = true
        else
          swal 'Must Include An Image for the Gift'
          $('a.create-reward').html('Create Inventory Item')
          scope.creating = false
          return
        formattedFields = {}
        if $('input[name=extra_fields]').val().trim() isnt ''
          fields = $('input[name=extra_fields]').val().split(",")
          num = 0
          for field in fields
            formattedFields[num] = field.trim()
            num++
          formattedFields = JSON.stringify(formattedFields)
        Bazaarboy.post 'rewards/create/', {profile:profileId, name:name, description:description, value:value, attachment:attachmentId, gif:useGif, extra_fields:formattedFields}, (response) ->
          if response.status is 'OK'
            swal
              type: "success"
              title: 'Inventory Created'
              text: 'You can now transfer this item to other organiztions for distribution to their audience, or you can add gifts to share with your own people.'
              , () ->
                Bazaarboy.redirect 'rewards/'
                return
          else
            $('a.create-reward').html('Create Inventory Item')
            scope.creating = false
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
    return

Bazaarboy.reward.new.init()