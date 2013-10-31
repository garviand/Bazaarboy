Bazaarboy.admin.login = 
    init: () ->
		$('.profile_login .profile_choices a').click (event) ->
			id = $(this).data('id')
			Bazaarboy.get 'admin/login/profile', {id:id}, (response) ->
				if response.status is 'OK'
					Bazaarboy.redirect 'index'
				else
					alert response.message
				return
			return
		return