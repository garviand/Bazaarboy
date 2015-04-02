Bazaarboy.list.sign_up =
    init: () ->
        scope = this
        $('form#sign-up-form').submit (e) ->
            e.preventDefault()
            params = {}
            params.sign_up = signup
            if $('input[name=first_name]').val().trim() == ''
                swal 'You Must Add a First Name'
                return
            params.first_name = $('input[name=first_name]').val()
            if $('input[name=last_name]').val().trim() == ''
                swal 'You Must Add a Last Name'
                return
            params.last_name = $('input[name=last_name]').val()
            if $('input[name=email]').val().trim() == ''
                swal 'You Must Add an Email'
                return
            params.email = $('input[name=email]').val()
            field_missing = false
            extra_fields = {}
            field_missing_name = ''
            $('input.extra-field').each () ->
                if $(this).val().trim() is ''
                    field_missing = true
                    field_missing_name = $(this).data('field')
                    console.log field_missing_name
                extra_fields[$(this).data('field')] = $(this).val()
                return
            if field_missing
                swal field_missing_name + ' Cannot Be Blank'
                $('input.submit-claim').val('Claim Reward!')
                scope.claiming = false
                return
            params.extra_fields = JSON.stringify(extra_fields)
            Bazaarboy.post 'lists/signup/submit/', params, (response) ->
                if response.status is 'OK'
                    swal
                        type: 'success'
                        title: 'Success!'
                        text: 'Your info has been submitted. Thanks!'
                        , () ->
                            $('input[type=text]').val('')
                            return
                else
                    swal
                        type: 'warning'
                        title: 'Oops!'
                        text: response.message
                return
            return
        return

Bazaarboy.list.sign_up.init()