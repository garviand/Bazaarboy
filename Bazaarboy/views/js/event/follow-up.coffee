Bazaarboy.event.follow_up =
    saving: false
    image: undefined
    pdf: undefined
    init: () ->
        scope = this
        if imgId?
            scope.image = {pk:imgId}
        if pdfId?
            scope.pdf = {pk:pdfId}
        # SELECT LISTS
        $('div.lists div.list').click () ->
            $(this).toggleClass 'active'
            return
        # PDF UPLOAD
        $('div#event-follow-up a.upload-attachment-btn').click () ->
            $('div#event-follow-up input[name=attachment_file]').click()
            return
        $('div#event-follow-up a.delete-attachment-btn').click () ->
            scope.pdf = undefined
            $('div.pdf-preview').addClass 'hide'
            $('div#event-follow-up a.upload-attachment-btn').css('display', 'block')
            $('div#event-follow-up a.delete-attachment-btn').css('display', 'none')
            return
        $('div#event-follow-up input[name=attachment_file]').fileupload
          url: rootUrl + 'event/followup/attachment/'
          type: 'POST'
          add: (event, data) ->
            csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val()
            console.log data
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
              scope.pdf = response.pdf
              $('div.pdf-preview span.filename').html(pdfName)
              $('div.pdf-preview').removeClass 'hide'
              $('div#event-follow-up a.upload-attachment-btn').css('display', 'none')
              $('div#event-follow-up a.delete-attachment-btn').css('display', 'block')
            else
              swal response.message
            return
        # IMAGE UPLOAD
        $('div#event-follow-up a.upload-image-btn').click () ->
            $('div#event-follow-up input[name=image_file]').click()
            return
        $('div#event-follow-up a.delete-image-btn').click () ->
            scope.image = undefined
            $('div#event-follow-up div.image-preview img').attr('src', '')
            $('div#event-follow-up div.image-preview').addClass 'hide'
            $('div#event-follow-up a.upload-image-btn').css('display', 'block')
            $('div#event-follow-up a.delete-image-btn').css('display', 'none')
            return
        $('div#event-follow-up input[name=image_file]').fileupload
            url: rootUrl + 'file/image/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                $('div#event-follow-up a.upload-image-btn').html 'Uploading...'
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    # Attempt to delete the last uploaded image
                    if scope.image?
                        Bazaarboy.post 'file/image/delete/', 
                            id: scope.image.pk
                    scope.image = response.image
                    $('div#event-follow-up a.upload-image-btn').html 'Upload Image'
                    $('div#event-follow-up div.image-preview').removeClass 'hide'
                    $('div#event-follow-up a.upload-image-btn').css('display', 'none')
                    $('div#event-follow-up a.delete-image-btn').css('display', 'block')
                    $('div#event-follow-up div.image-preview img').attr('src', mediaUrl + response.image.source)
                else
                    alert response.message
                    $('div#event-follow-up a.upload-image-btn').html 'Upload Image'
                return
        # BUTTON TYPE SELECTION
        $('a.button-type-btn').click () ->
            $('a.button-type-btn').removeClass('primary-btn')
            $('a.button-type-btn').addClass('primary-btn-inverse')
            $('a.button-type-btn').removeClass('active')
            $(this).addClass('active')
            $(this).addClass('primary-btn')
            $(this).removeClass('primary-btn-inverse')
            $('div.custom-link').addClass('hide')
            if $(this).data('type') == 'link'
                $('div.custom-link').removeClass('hide')
            return
        # COLOR PICKER
        $('input[name=colorpicker]').spectrum
            preferredFormat: "hex"
            showInput: true
            showButtons: true
        # SAVE & PREVIEW
        $('a.save-follow-up').click () ->
            if not scope.saving
                $('a.save-follow-up').html 'Saving...'
                scope.saving = true
                if not followUpEdit
                    targetId = $('div.email input[name=event]').val()
                    targetUrl = 'event/followup/new/'
                else
                    targetId = $('div.email input[name=follow_up]').val()
                    targetUrl = 'event/followup/save/'
                heading = $('div.email textarea[name=heading]').val()
                if heading.trim() is ''
                    swal("Wait!", "Email Header Cannot Be Empty", "warning")
                    scope.saving = false
                    $('a.save-follow-up').html 'Save &amp; Preview'
                    return
                message = $('div.email textarea[name=message]').val()
                if message.trim() is ''
                    swal("Wait!", "Email Message Cannot Be Empty", "warning")
                    scope.saving = false
                    $('a.save-follow-up').html 'Save &amp; Preview'
                    return
                button_text = $('div.email input[name=button_text]').val()
                if button_text.trim() is ''
                    swal("Wait!", "Email Button Text Cannot Be Empty", "warning")
                    scope.saving = false
                    $('a.save-follow-up').html 'Save &amp; Preview'
                    return
                activeLists = $('div.lists div.list.active')
                if activeLists.length is 0
                    swal("Wait!", "You Must Select At Least 1 Ticket", "warning")
                    scope.saving = false
                    $('a.save-follow-up').html 'Save &amp; Preview'
                    return
                lists = ''
                for list in activeLists
                    if lists != ''
                        lists += ', '
                    lists += $(list).data('id')
                imageId = ''
                deleteImg = true
                if scope.image?
                    imageId = scope.image.pk
                    deleteImg = false
                deletePdf = true
                if scope.pdf?
                    pdfId = scope.pdf.pk
                    deletePdf = false
                color = $('input[name=colorpicker]').spectrum("get").toHexString()
                button_type = $('a.button-type-btn.active').data('type')
                custom_url = $('input[name=button_link]').val()
                if button_type == 'link' and not(/^([a-z]([a-z]|\d|\+|-|\.)*):(\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?((\[(|(v[\da-f]{1,}\.(([a-z]|\d|-|\.|_|~)|[!\$&'\(\)\*\+,;=]|:)+))\])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=])*)(:\d*)?)(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*|(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)|((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)){0})(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(custom_url))
                    scope.saving = false
                    $('a.save-follow-up').html 'Save &amp; Preview'
                    swal "Custom Link is not valid. Remember, you must include http:// or https://."
                    return
                Bazaarboy.post targetUrl, {id:targetId, heading:heading, message:message, button_text:button_text, button_type:button_type, custom_link:custom_url, tickets:lists, color:color, image:imageId, deleteImg:deleteImg, pdf:pdfId, deletePdf:deletePdf}, (response) ->
                    if response.status is 'OK'
                        followUpId = response.follow_up.pk
                        Bazaarboy.redirect 'event/followup/' + followUpId + '/preview'
                        return
                    else
                      swal response.message
                    scope.saving = false
                    $('a.save-follow-up').html 'Save &amp; Preview'
                    return
            return
        return
        
Bazaarboy.event.follow_up.init()