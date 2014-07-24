Bazaarboy.list.list =
    uploads:
        csv: undefined
    init: () ->
        scope = this
        # ADD SINGLE ITEM
        $('div#list-management div.controls a.add-single-item').click () ->
            $('div#add-item-modal').foundation('reveal', 'open')
            return
        $('a.add-item-close').click () ->
            $('div#add-item-modal').foundation('reveal', 'close')
            return
        $('div#add-item-modal form.add-item-form').on 'valid.fndtn.abide', () ->
            $('div#add-item-modal div.submit-add-item a.add-item-submit').html 'Adding...'
            params = $('div#add-item-modal form.add-item-form').serializeObject()
            params.id = listId
            Bazaarboy.post 'list/add/item/', params, (response) ->
                if response.status is 'OK'
                    new_item = $('div#list-management div.list div.list-item.template').clone()
                    new_item.find('div.name').html response.item.first_name + " " + response.item.last_name
                    new_item.find('div.email').html response.item.email
                    new_item.removeClass 'template'
                    new_item.removeClass 'hide'
                    $('div#list-management div.list .list-items').prepend new_item
                    $('div#add-item-modal div.submit-add-item div.message').html 'Added!'
                    setTimeout -> 
                        $('div#add-item-modal div.submit-add-item div.message').html '&nbsp;'
                    , 3000
                    $('div#add-item-modal div.submit-add-item a.add-item-submit').html 'Add To List'
                    $('div#add-item-modal form.add-item-form input').val ''
                    $('div#add-item-modal form.add-item-form textarea').val ''
                else
                    $('div#add-item-modal div.submit-add-item div.message').html response.message
                    setTimeout -> 
                        $('div#add-item-modal div.submit-add-item div.message').html '&nbsp;'
                    , 3000
                    $('div#add-item-modal div.submit-add-item a.add-item-submit').html 'Add To List'
                return
        $('div#add-item-modal a.add-item-submit').click () ->
            $('div#add-item-modal form.add-item-form').submit()
            return
        # ADD FROM EVENT
        $('div#list-management div.controls a.add-from-event').click () ->
            $('div#add-event-modal').foundation('reveal', 'open')
            return
        $('a.add-event-close').click () ->
            $('div#add-event-modal').foundation('reveal', 'close')
            return
        $('div#add-event-modal form.add-event-form div.event-list').click () ->
            $(this).toggleClass 'selected'
            return
        $('div#add-event-modal form.add-event-form a.add-event-submit').click () ->
            $('div#add-event-modal form.add-event-form a.add-event-submit').html 'Adding...'
            selected_events = $('div#add-event-modal form.add-event-form div.row.event-list.selected')
            num_events = selected_events.length
            num_added = 0
            console.log num_events
            $.each selected_events, (event) ->
                Bazaarboy.post 'list/add/event/', {id:listId, event:$(this).data('id')}, (response) ->
                    num_added++
                    if response.status is 'OK'
                        if num_added == num_events
                            $('div#add-event-modal form.add-event-form').addClass 'hide'
                            $('div#add-event-modal div.add-event-success').removeClass 'hide'
                            setTimeout -> 
                                location.reload()
                            , 2500
                    else
                        alert response.message
                        $('div#add-event-modal form.add-event-form a.add-event-submit').html 'Add To List'
                    return
                return
            return
        # CSV UPLOAD
        $('div#list-management div.controls a.upload-csv-btn').click () ->
            $('div#list-management form.upload_csv input[name=csv_file]').click()
            return
        $('div.csv_upload_interface div.csv-controls a.cancel-csv-btn').click () ->
            $('div.csv_upload_interface').addClass 'hide'
            $('div.csv_upload_interface div.upload_row:not(.template)').remove()
            return
        $('body').on 'change', 'div.csv_upload_interface select[name=field]', () ->
            if $(this).val() is 'none'
                $(this).parents('div.upload_row').removeClass 'active'
            else
                $(this).parents('div.upload_row').addClass 'active'
            $(this).parents('div.csv_upload_interface').find('select[name=field] option').attr('disabled', false)
            $(this).parents('div.csv_upload_interface').find('div.upload_row.active select[name=field] option:selected').each () ->
                $(this).parents('div.csv_upload_interface').find('select[name=field] option[value='+$(this).val()+']').attr('disabled', true)
                return
            return
        $('body').on 'click', 'div.csv_upload_interface div.csv-controls a.submit-csv-btn', () ->
            button = $(this)
            button.html 'Adding...'
            id = listId
            csv = scope.uploads.csv.pk
            format = {}
            $('div.csv_upload_interface div.upload_row.active select[name=field] option:selected').each () ->
                format[$(this).val()] = $(this).parents('div.upload_row').data('col')
            if not format.hasOwnProperty('email')
                $('div.csv_upload_interface div.csv-controls div.error-message').html 'You Must Select an EMAIL Column'
                setTimeout -> 
                    $('div.csv_upload_interface div.csv-controls div.error-message').html '&nbsp;'
                , 5000
                button.html 'Submit'
                return
            if not format.hasOwnProperty('first_name')
                $('div.csv_upload_interface div.csv-controls div.error-message').html 'You Must Select a FIRST_NAME Column'
                setTimeout -> 
                    $('div.csv_upload_interface div.csv-controls div.error-message').html '&nbsp;'
                , 5000
                button.html 'Submit'
                return
            format = JSON.stringify format 
            Bazaarboy.post 'list/add/csv/', {id:id, csv:csv, format:format}, (response) ->
                if response.status is 'OK'
                    $('div.csv_upload_interface div.csv-controls div.error-message').html 'CSV Uploaded Succesfully. Refreshing List.....'
                    $('div.csv_upload_interface div.csv-controls a').hide()
                    setTimeout -> 
                        $("html, body").animate
                            scrollTop: 0
                        , 1
                        location.reload()
                    , 2500
                else
                    $('div.csv_upload_interface div.csv-controls div.error-message').html response.message
                    setTimeout -> 
                        $('div.csv_upload_interface div.csv-controls div.error-message').html '&nbsp;'
                    , 5000
                button.html 'Submit'
                return
            return
        $('div#list-management form.upload_csv input[name=csv_file]').fileupload
            url: rootUrl + 'file/csv/upload/'
            type: 'POST'
            add: (event, data) =>
                data.submit()
                return
            done: (event, data) =>
                response = jQuery.parseJSON data.result
                if response.status is 'OK'
                    scope.uploads.csv = response.file
                    Bazaarboy.post 'list/csv/prepare/', {csv: response.file.pk}, (response) =>
                        if response.status is 'OK'
                            results = response.results
                            results_rows = Object.keys(results).length
                            if results_rows > 0
                                final_results = []
                                results_columns = results[0].length
                                for i in [0..results_columns-1]
                                    final_results[i] = []
                                for i in [0..results_columns-1]
                                    for j in [0..2]
                                        final_results[i][j] = results[j][i]
                                for result, num in final_results
                                    new_row = $("div.csv_upload_interface div.upload_row.template").clone()
                                    new_row.attr 'data-col', num
                                    new_row.find('div.col-1').html result[0]
                                    new_row.find('div.col-2').html result[1]
                                    new_row.find('div.col-3').html result[2]
                                    new_row.removeClass 'hide'
                                    new_row.removeClass 'template'
                                    $("div.csv_upload_interface div.upload_rows").append(new_row)
                                $('div.csv_upload_interface').removeClass 'hide'
                                $("html, body").animate
                                    scrollTop: $("div.csv_upload_interface").offset().top
                                , 500
                            else
                                alert 'There are no rows in this CSV!'
                        else
                            alert response.message
                        return
                else
                    alert response.message
                return
        return

Bazaarboy.list.list.init()