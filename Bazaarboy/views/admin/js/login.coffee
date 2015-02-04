Bazaarboy.admin.login = 
    init: () ->
        $(document).ready () ->
            $('form[name=login]').submit (event) ->
                event.preventDefault()
                if $('form[name=login] input[name=name]').val().length is 0 or
                    $('form[name=login] input[name=password]').val().length is 0
                   return
                params = $('form[name=login]').serialize()
                Bazaarboy.get 'admin/auth/', params, (response) ->
                    if response.status is 'OK'
                        Bazaarboy.redirect 'admin/'
                    else
                        $('form[name=login] a.btn').addClass('btn-danger')
                        $('form[name=login] a.btn').html('Access Denied')
                    return
                return
            $('form[name=login] a.btn').click () ->
                $('form[name=login]').submit()
                return
            $('form[name=login] input').keyup (event) ->
                if event.keyCode is 13
                    event.preventDefault()
                    $('form[name=login]').submit()
                else
                    $('form[name=login] a.btn').removeClass('btn-danger')
                    $('form[name=login] a.btn').html('Login')
                return
            return
        return

Bazaarboy.admin.login.init()