Bazaarboy.list.manage_sign_up =
    init: () ->
        scope = this
        # SEND REWARD
        $('a.reward-member').click () ->
            $("div#rewards-modal").foundation('reveal', 'open')
            $("div#rewards-modal input[name=reward_email]").val($(this).data('email'))
            $("div#rewards-modal span.reward-reciever").html($(this).data('first') + ' ' + $(this).data('last'))
            return
        $('a.send-reward').click () ->
            button = $(this)
            button.html 'Sending...'
            rewardId = $(this).data('id')
            rewardEmail = $("div#rewards-modal input[name=reward_email]").val()
            rewardMessage = $('div#rewards-modal textarea[name=message]').val()
            quantityElement = $(this).closest('.reward').find('span.quantity')
            quantityAmount = parseInt(quantityElement.html())
            Bazaarboy.post 'rewards/claim/add/', {item:rewardId, email:rewardEmail, message:rewardMessage}, (response) ->
                if response.status is 'OK'
                    swal
                        type: 'success'
                        title: 'Reward Sent'
                        text: 'The reward has been sent.'
                    quantityElement.html(quantityAmount - 1)
                    $('div.gifted[data-email="' + rewardEmail + '"]').removeClass('hide')
                    $("div#rewards-modal").foundation('reveal', 'close')
                    button.html 'Send Reward'
                else
                    swal response.message
                    button.html 'Send Reward'
                return
        # RAFFLE
        $("a.raffle-btn").click (e) ->
            e.preventDefault()
            winner_id = Math.floor(Math.random()*($("div.sign-ups div.sign-up").length))
            winner = $('div.sign-ups div.sign-up').eq(winner_id)
            winner_name = winner.attr('data-name')
            winner_email = winner.attr('data-email')
            $('div#raffle-modal div.subtext-name').html(winner_name)
            $('div#raffle-modal div.subtext-email').html(winner_email)
            $('div#rewards-modal input[name=reward_email]').val(winner_email)
            $('div#rewards-modal span.reward-reciever').html(winner_name)
            $('div#raffle-modal').foundation('reveal', 'open')
            return
        $('a.show-rewards-btn').click () ->
            $("div#rewards-modal").foundation('reveal', 'open')
            return
        # ADD TO LIST
        $('a.add-to-list-btn').click (e) ->
            $('div#add-list-modal').foundation('reveal', 'open')
            return
        $('div#add-list-modal a.add-cancel-btn').click (e) ->
            $('div#add-list-modal').foundation('reveal', 'close')
            return
        $('a.add-to-list-single-btn').click (e) ->
            $('div#add-list-single-modal input[name=email]').val($(this).data('email'))
            $('div#add-list-single-modal input[name=first_name]').val($(this).data('first'))
            $('div#add-list-single-modal input[name=last_name]').val($(this).data('last'))
            $('div#add-list-single-modal').foundation('reveal', 'open')
            return
        $('div#add-list-single-modal a.add-cancel-btn').click (e) ->
            $('div#add-list-single-modal').foundation('reveal', 'close')
            return
        $('body').on 'click', 'div#add-list-modal div.list, div#add-list-single-modal div.list', (e) ->
            $(this).toggleClass 'active'
            return
        $('div#add-list-modal a.create-list').click () ->
            $('div#add-list-modal div.status').html 'Creating...'
            $('div#add-list-modal div.submit-actions a').css('display','none')
            profileId = $('div#add-list-modal input[name=profile_id]').val()
            signupId = $('div#add-list-modal input[name=signup_id]').val()
            list_name = $('div#add-list-modal input[name=list_name]').val()
            if list_name.trim() isnt ''
                Bazaarboy.post 'lists/create/', {profile:profileId, name:list_name, is_hidden:1}, (response) ->
                    if response.status is 'OK'
                        listId = response.list.pk
                        $('div#add-list-modal div.status').html 'Successfully Created List! Adding Members...'
                        Bazaarboy.post 'lists/add/signup/', {id:listId, signup:signupId}, (response) ->
                            if response.status is 'OK'
                                newList = $('div.list-template').clone()
                                newList.attr('data-id', response.list.pk)
                                newList.find('div.list-name').html(response.list.name)
                                newList.find('div.list-action').html(response.added + ' Members')
                                newList.removeClass('hide')
                                $('div#add-list-modal div.lists').prepend(newList)
                                $('div#add-list-modal div.status').html 'Congrats! List was Created and ' + response.added + ' People were added.'
                            else
                                swal 'List Was Created, But there was an error: ' + response.message
                            $('div#add-list-modal div.submit-actions a').css('display','block')
                            return
                    else
                        swal 'Could not create list'
                        $('div#add-list-modal div.submit-actions a').css('display','block')
                    $('div#add-list-modal input[name=list_name]').val('')
                    return
            else
                swal 'List name can\'t be empty'
                $('div#add-list-modal div.submit-actions a').css('display','block')
            return
        $('div#add-list-modal a.submit-add-btn').click () ->
            $('div#add-list-modal div.status').html 'Adding People to Lists...'
            $('div#add-list-modal div.submit-actions a').css('display','none')
            signupId = $('div#add-list-modal input[name=signup_id]').val()
            selected_lists = $('div#add-list-modal div.lists div.list.active')
            num_lists = selected_lists.length
            error_lists = 0
            num_finished = 0
            if num_lists > 0
                $.each selected_lists, (list) ->
                    Bazaarboy.post 'lists/add/signup/', {id:$(this).data('id'), signup:signupId}, (response) ->
                        if response.status is 'OK'
                            $('div#add-list-modal div.status').html(num_finished + ' Lists Complete - ' + (num_lists - num_finished) + ' Lists Remaining')
                        else
                            error_lists++
                        num_finished++
                        if (num_lists - num_finished) is 0
                            if error_lists > 0
                                swal 'Lists added, but some people may have been left out'
                            else
                                swal
                                    title: "Success"
                                    text: "The Sign Ups have been Added!"
                                    type: "success"
                                    , ->
                                        $('div#add-list-modal').foundation('reveal', 'close')
                                        return
                            $('div#add-list-modal div.status').html '&nbsp;'
                            $('div#add-list-modal div.submit-actions a').css('display','block')
                        return
                    return
            else
                swal 'You Must Select at least One List!'
            return
        $('div#add-list-single-modal a.submit-add-btn').click () ->
            $('div#add-list-single-modal div.status').html 'Adding People to Lists...'
            $('div#add-list-single-modal div.submit-actions a').css('display','none')
            signupId = $('div#add-list-single-modal input[name=signup_id]').val()
            selected_lists = $('div#add-list-single-modal div.lists div.list.active')
            thisEmail = $('div#add-list-single-modal input[name=email]').val()
            thisFirst = $('div#add-list-single-modal input[name=first_name]').val()
            thisLast = $('div#add-list-single-modal input[name=last_name]').val()
            num_lists = selected_lists.length
            error_lists = 0
            num_finished = 0
            if num_lists > 0
                $.each selected_lists, (list) ->
                    Bazaarboy.post 'lists/add/item/', {id:$(this).data('id'), email:thisEmail, first_name:thisFirst, last_name:thisLast}, (response) ->
                        if response.status is 'OK'
                            $('div#add-list-single-modal div.status').html(num_finished + ' Lists Complete - ' + (num_lists - num_finished) + ' Lists Remaining')
                        else
                            error_lists++
                        num_finished++
                        if (num_lists - num_finished) is 0
                            if error_lists > 0
                                swal 'Lists added, but some errors may have occured'
                            else
                                swal
                                    title: "Success"
                                    text: "Added to lists!"
                                    type: "success"
                                    , ->
                                        $('div#add-list-single-modal').foundation('reveal', 'close')
                                        return
                            $('div#add-list-single-modal div.status').html '&nbsp;'
                            $('div#add-list-single-modal div.submit-actions a').css('display','block')
                        return
                    return
            else
                swal 'You Must Select at least One List!'
            return
        return

Bazaarboy.list.manage_sign_up.init()