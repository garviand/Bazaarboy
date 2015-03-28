Bazaarboy.event.follow_up_preview =
    sending: false
    sendEmail: (followUpId) ->
        Bazaarboy.post 'event/followup/send/', {id:followUpId}, (response) ->
            if response.status is 'OK'
                console.log response
                Bazaarboy.redirect 'event/followup/' + response.follow_up.pk + '/details/'
            else if response.status is 'SUBSCRIBE'
                $('div#add-subscription-modal').foundation('reveal', 'open')
            else if response.status is 'PAYMENT'
                StripeCheckout.open
                    key: response.publishable_key
                    address: false
                    amount: response.cost
                    currency: 'usd'
                    name: 'Send Follow Ups'
                    description: response.sent + ' Follow Ups - ' + response.event.name
                    panelLabel: 'Send Now'
                    image: 'https://bazaarboy.s3.amazonaws.com/static/images/logo-big.png'
                    closed: () ->
                        Bazaarboy.event.follow_up_preview.sending = false
                        $('div.email-actions a.send-email').html 'Send Email'
                        return
                    token: (token) =>
                        Bazaarboy.post 'payment/charge/followup/', 
                            follow_up: response.follow_up.pk
                            stripe_token: token.id
                            amount: response.cost
                        , (response) =>
                            if response.status is 'OK'
                                Bazaarboy.event.follow_up_preview.sending = true
                                $('div.email-actions a.send-email').html 'Sending...'
                                Bazaarboy.event.follow_up_preview.sendEmail(response.follow_up.pk)
                            else
                                swal response.message
                                Bazaarboy.event.follow_up_preview.sending = false
                                $('div.email-actions a.send-email').html 'Send Email'
                            return
                        return
            else
                swal response.message
                Bazaarboy.event.follow_up_preview.sending = false
                $('div.email-actions a.send-email').html 'Send Email'
            return
        return
    init: () ->
        scope = this
        $('a.cancel-subscription').click () ->
            $('div#add-subscription-modal').foundation('reveal', 'close')
            return
        $('div#add-subscription-modal a.create-subscription').click () ->
            StripeCheckout.open
                key: publishableKey
                address: false
                amount: 0
                currency: 'usd'
                name: 'Bazaarboy Gifts Account'
                description: 'Create Account'
                panelLabel: 'Subscribe'
                closed: () ->
                    $('div#add-subscription-modal').foundation('reveal', 'close')
                    return
                token: (token) =>
                    Bazaarboy.post 'rewards/subscribe/',
                        stripe_token: token.id
                        email: token.email
                        profile: profileId
                        , (response) =>
                            if response.status is 'OK'
                                swal
                                    type: "success"
                                    title: 'Subscribed!'
                                    text: 'You have successfully subscribed for a Bazaarboy account!'
                                    , () ->
                                        location.reload()
                                        return
                            else
                                alert response.message
                            return
            return
        $('div.email-actions a.send-email').click () ->
            if not scope.sending
                $(this).html 'Sending...'
                scope.sending = true
                followUpId = $(this).data('id')
                scope.sendEmail(followUpId)
            return
        $(document).on 'closed.fndtn.reveal', 'div#add-subscription-modal', () ->
            Bazaarboy.event.follow_up_preview.sending = false
            $('div.email-actions a.send-email').html 'Send Email'
            return
        return
        
Bazaarboy.event.follow_up_preview.init()