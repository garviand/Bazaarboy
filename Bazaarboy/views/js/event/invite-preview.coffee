Bazaarboy.event.invite_preview =
    sending: false
    sendEmail: (inviteId) ->
        Bazaarboy.post 'event/invite/send/', {id:inviteId}, (response) ->
            if response.status is 'OK'
                Bazaarboy.redirect 'event/invite/' + response.invite.pk + '/details/'
            else if response.status is 'PAYMENT'
                StripeCheckout.open
                    key: response.publishable_key
                    address: false
                    amount: response.cost
                    currency: 'usd'
                    name: 'Send Invitations'
                    description: response.sent + ' Invitations - ' + response.invite.event.name
                    panelLabel: 'Send Now'
                    image: 'https://bazaarboy.s3.amazonaws.com/static/images/logo-big.png'
                    closed: () ->
                        Bazaarboy.event.invite_preview.sending = false
                        $('div.email-actions a.send-email').html 'Send Email'
                        return
                    token: (token) =>
                        Bazaarboy.post 'payment/charge/invite/', 
                            invite: response.invite.pk
                            stripe_token: token.id
                            amount: response.cost
                        , (response) =>
                            if response.status is 'OK'
                                Bazaarboy.event.invite_preview.sending = true
                                $('div.email-actions a.send-email').html 'Sending...'
                                Bazaarboy.event.invite_preview.sendEmail(response.invite.pk)
                            else
                                swal response.message
                                Bazaarboy.event.invite_preview.sending = false
                                $('div.email-actions a.send-email').html 'Send Email'
                            return
                        return
            else
                swal response.message
                Bazaarboy.event.invite_preview.sending = false
                $('div.email-actions a.send-email').html 'Send Email'
            return
        return
    init: () ->
        scope = this
        $('div.email-actions a.send-email').click () ->
            if not scope.sending
                swal
                    title: "Confirm Details"
                    html: "Title: " + eventName + "<br /><br />Date: " + eventDate + "<br /><br />Recipients: " + sentNumber
                    type: "success"
                    showCancelButton: true
                    confirmButtonText: "Send Email"
                    closeOnConfirm: true
                    , (isConfirm) =>
                        if isConfirm
                            $(this).html 'Sending...'
                            scope.sending = true
                            inviteId = $(this).data('id')
                            scope.sendEmail(inviteId)
            return
        return
        
Bazaarboy.event.invite_preview.init()