Bazaarboy.admin.login =
	filterProfiles: (value) ->
		length = $('.profile_login .profile_choices a').length
		for i in [0..length-1]
			profile = $('.profile_login .profile_choices a:eq(' + i + ')')
			targetValue = $(profile).html()
			if targetValue.toLowerCase().indexOf(value.toLowerCase()) != -1
				$(profile).removeClass('hidden')
		return
	filterEvents: (value) ->
		length = $('div.event_export .event_choices a').length
		for i in [0..length-1]
			event = $('div.event_export .event_choices a:eq(' + i + ')')
			targetValue = $(event).html()
			if targetValue.toLowerCase().indexOf(value.toLowerCase()) != -1
				$(event).removeClass('hidden')
		return
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
		$('.profile_login .input_container input[name=profile_name]').keyup (event) =>
			event.preventDefault()
			if $('.profile_login .input_container input[name=profile_name]').val() == ''
				$('.profile_login .profile_choices a').removeClass('hidden')
			else
				$('.profile_login .profile_choices a').addClass('hidden')
				@filterProfiles($('.profile_login .input_container input[name=profile_name]').val())
			return
		$('div.event_export .input_container input[name=event_name]').keyup (event) =>
			event.preventDefault()
			if $('div.event_export .input_container input[name=event_name]').val() == ''
				$('div.event_export .event_choices a').removeClass('hidden')
			else
				$('div.event_export .event_choices a').addClass('hidden')
				@filterEvents($('div.event_export .input_container input[name=event_name]').val())
			return
		return

Bazaarboy.admin.login.init()