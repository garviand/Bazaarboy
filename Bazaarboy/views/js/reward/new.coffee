Bazaarboy.reward.new =
  attachment: undefined
  init: () ->
    scope = this
    $('a.create-reward').click () ->
      if $('input[name=name]').val().trim() is ''
        swal 'Name Cannot Be Blank'
        return
      name = $('input[name=name]').val()
      if $('textarea[name=description]').val().trim() is ''
        swal 'Description Cannot Be Blank'
        return
      description = $('textarea[name=description]').val()
      if $('textarea[name=details]').val().trim() is ''
        swal 'Details Cannot Be Blank'
        return
      details = $('textarea[name=details]').val()
      if scope.attachment?
        attachmentId = scope.attachment.pk
      else
        attachmentId = ''
      Bazaarboy.post 'reward/create/', {profile:profileId, name:name, description:description, details:details, attachment:attachmentId}, (response) ->
        if response.status is 'OK'
          console.log response
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
        if data.files[0].type not in ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/gif']
          swal 'Must Be A PDF, PNG, JPG or GIF'
        else
          data.submit()
        return
      done: (event, data) ->
        pdfName = data.files[0].name
        response = jQuery.parseJSON data.result
        if response.status is 'OK'
          scope.attachment = response.pdf
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