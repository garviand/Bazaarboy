Bazaarboy.list.list =
    uploads:
        csv: undefined
    submitting: false
    init: () ->
        scope = this
        # REWARD 
        $('a.reward-member').click () ->
            $("div#rewards-modal").foundation('reveal', 'open')
            $("div#rewards-modal input[name=reward_email]").val($(this).data('email'))
            $("div#rewards-modal span.reward-reciever").html($(this).data('name'))
            return
        $('a.send-reward').click () ->
            button = $(this)
            button.html 'Sending...'
            rewardId = $(this).data('id')
            rewardEmail = $("div#rewards-modal input[name=reward_email]").val()
            quantityElement = $(this).closest('.reward').find('span.quantity')
            quantityAmount = parseInt(quantityElement.html())
            Bazaarboy.post 'rewards/claim/add/', {item:rewardId, email:rewardEmail}, (response) ->
                if response.status is 'OK'
                    swal
                        type: 'success'
                        title: 'Reward Sent'
                        text: 'The reward has been sent.'
                    quantityElement.html(quantityAmount - 1)
                    $("div#rewards-modal").foundation('reveal', 'close')
                    button.html 'Send Reward'
                else
                    swal response.message
                    button.html 'Send Reward'
                return
        # REMOVE LIST MEMBER
        $('div.list').on 'click', 'a.remove-member', () ->
            member = $(this).closest('div.list-item')
            member_id = $(this).data('id')
            console.log member_id
            if confirm 'Are you sure you want to remove this person?'
                Bazaarboy.post 'lists/remove/item/', {id:member_id}, (response) ->
                    if response.status is 'OK'
                        member.remove()
                        member_count = parseInt($('span.member-count').html()) - 1
                        $('span.member-count').html(member_count)
                    else
                        alert response.message
                    return
            return
        # ADD MEMBERS BUTTON INTERACTIONS
        $('a.start-member-add').click () ->
            $('a.start-member-add').removeClass 'secondary-btn'
            $('a.start-member-add').removeClass 'active'
            $('a.start-member-add').addClass 'secondary-btn-inverse'
            $(this).removeClass 'secondary-btn-inverse'
            $(this).addClass 'active'
            $(this).addClass 'secondary-btn'
            $('div.member-add-interface').addClass 'hide'
            $('a.cancel-add').css('display', 'block')
            return
        $('a.cancel-add').click () ->
            $('a.start-member-add').removeClass 'secondary-btn'
            $('a.start-member-add').removeClass 'active'
            $('a.start-member-add').addClass 'secondary-btn-inverse'
            $('div.member-add-interface').addClass 'hide'
            $(this).css('display', 'none')
            return
        $('div.list-controls a.add-from-csv').click () ->
            $('div.member-add-interface').addClass 'hide'
            $('div.csv_upload_interface').removeClass 'hide'
            return
        $('div.list-controls a.add-from-event').click () ->
            $('div.member-add-interface').addClass 'hide'
            $('div.event-add-interface').removeClass 'hide'
            return
        $('div.list-controls a.add-single-item').click () ->
            $('div.member-add-interface').addClass 'hide'
            $('div.manual-add-interface').removeClass 'hide'
            return
        # MANUAL ADD
        $('div.manual-add-interface a.add-member-submit').click () ->
            $('div.manual-add-interface a.add-member-submit').html 'Adding...'
            params = $('div.manual-add-interface form.add-item-form').serializeObject()
            params.id = listId
            Bazaarboy.post 'lists/add/item/', params, (response) ->
                if response.status is 'OK'
                    console.log response
                    new_item = $('div#list-management div.list div.list-item.template').clone()
                    new_item.find('div.name').html response.item.first_name + " " + response.item.last_name + "&nbsp;"
                    new_item.find('div.email').html response.item.email
                    new_item.find('a.reward-member').attr('data-email', response.item.email)
                    new_item.find('a.reward-member').attr('data-name', response.item.first_name + " " + response.item.last_name)
                    new_item.find('a.remove-member').attr('data-id', response.item.pk)
                    new_item.removeClass 'template'
                    new_item.removeClass 'hide'
                    $('div#list-management div.list .list-items').prepend new_item
                    $('div.manual-add-interface a.add-member-submit').html 'Success!'
                    $('div.manual-add-interface input[type=text]').val('')
                    $('div.manual-add-interface textarea').val('')
                    $('div.manual-add-interface textarea').html('')
                    setTimeout -> 
                        $('div.manual-add-interface a.add-member-submit').html 'Add Member'
                    , 1000
                else
                    alert response.message
                return
            return
        # ADD FROM EVENT
        $('div.event-add-interface div.event-list div.event').click () ->
            $(this).toggleClass 'active'
            return
        $('div.event-add-interface a.cancel-event-add').click () ->
            $('a.cancel-add').click()
        $('div.event-add-interface a.submit-event-add').click () ->
            if not scope.submitting
                $(this).addClass 'disabled-btn'
                $(this).html 'Adding...'
                scope.submitting = true
                selected_events = $('div.event-add-interface div.event-list div.event.active')
                num_events = selected_events.length
                num_added = 0
                added_members = 0
                duplicate_members = 0
                if num_events > 0
                    $.each selected_events, (event) ->
                        Bazaarboy.post 'lists/add/event/', {id:listId, event:$(this).data('id')}, (response) ->
                            added_members += response.added
                            duplicate_members += response.duplicates
                            num_added++
                            if response.status is 'OK'
                                if num_added == num_events
                                    $('div.event-add-interface div.event-add-controls div.error-message').html 'Members: <span style="font-weight:bold;"> ' + added_members + '</span> Added -  <span style="font-weight:bold;">' + duplicate_members + '</span> Duplicates. Refreshing List, this may take a minute.....'
                                    $('div.event-add-interface div.event-add-controls a').hide()
                                    setTimeout -> 
                                        location.reload()
                                    , 2500
                            else
                                alert response.message
                                $(this).removeClass 'disabled-btn'
                                $(this).html 'Confirm'
                                scope.submitting = false
                            return
                        return
                else
                    alert 'Must Select At Least 1 Event!'
                    $(this).removeClass 'disabled-btn'
                    $(this).html 'Confirm'
                    scope.submitting = false
            return
        # CSV UPLOAD
        $('div#list-management div.member-add-interface a.upload-csv-btn').click () ->
            $('div#list-management form.upload_csv input[name=csv_file]').click()
            $('div.csv_upload_interface').find('select[name=field] option').attr('disabled', false)
            return
        $('div.csv_upload_interface a.cancel-csv-upload').click () ->
            $('div.csv_upload_interface').addClass 'hide'
            $('div.csv_upload_interface div.upload_row:not(.template)').remove()
            $('div.csv_upload_interface div.upload-btn-container').removeClass 'hide'
            $('div.csv_upload_interface div.csv-info-container').addClass 'hide'
            $('div.csv_upload_interface div.upload_rows').addClass 'hide'
            $('div.csv_upload_interface div.title_rows').addClass 'hide'
            $('div.member-add-interface').addClass 'hide'
            $('div.csv_upload_interface div.csv-controls').addClass 'hide'
            $('a.cancel-add').css('display', 'none')
            $('div.csv_upload_interface').find('select[name=field] option').attr('disabled', false)
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
            if not scope.submitting
                scope.submitting = true
                button = $(this)
                button.html 'Adding...'
                button.addClass 'disabled-btn'
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
                    scope.submitting = false
                    button.removeClass 'disabled-btn'
                    return
                format = JSON.stringify format 
                Bazaarboy.post 'lists/add/csv/', {id:id, csv:csv, format:format}, (response) ->
                    if response.status is 'OK'
                        $('div.csv_upload_interface div.csv-controls div.error-message').html 'Members: <span style="font-weight:bold;"> ' + response.added + '</span> Added -  <span style="font-weight:bold;">' + response.duplicates + '</span> Duplicates. Refreshing List, this may take a minute.....'
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
                    scope.submitting = false
                    button.removeClass 'disabled-btn'
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
                    filename = response.filename
                    Bazaarboy.post 'lists/csv/prepare/', {csv: response.file.pk}, (response) =>
                        if response.status is 'OK'
                            $('div.csv_upload_interface div.csv-info-container div.csv-name').html(filename)
                            $('div.csv_upload_interface div.upload-btn-container').addClass 'hide'
                            $('div.csv_upload_interface div.csv-info-container').removeClass 'hide'
                            $('div.csv_upload_interface div.upload_rows').removeClass 'hide'
                            $('div.csv_upload_interface div.title_rows').removeClass 'hide'
                            $('div.csv_upload_interface div.csv-controls').removeClass 'hide'
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