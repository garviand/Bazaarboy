Bazaarboy.admin.login =
	searchProfiles: (value) ->
		Bazaarboy.get 'profile/search/', {keyword: value}, (response) ->
			if response.status is 'OK'
				profiles = response.profiles
				console.log profiles
				if profiles.length > 0
					$('.profile_login .profile_choices').empty()
					for i in [0..profiles.length-1]
						$('.profile_login .profile_choices')
							.append('<a href="javascript:;" data-id="' + profiles[i].pk + '">' + profiles[i].name + '</a>')
				else
					$('.profile_login .profile_choices').empty()
			return
		return
	searchEvents: (value) ->
		Bazaarboy.get 'event/search/', {keyword: value}, (response) ->
			if response.status is 'OK'
				events = response.events
				if events.length > 0
					$('.event_export .event_choices').empty()
					for i in [0..events.length-1]
						$('.event_export .event_choices')
							.append('<a href="/event/export/csv?id=' + events[i].pk + '">' + events[i].name + '</a>')
			return
		return
	init: () ->
		$('div.colorpicker').spectrum
			preferredFormat: "hex"
			flat: true
			showInput: true
			showButtons: false
		$('a.create-premium-event').click () ->
			color = $('div.colorpicker').spectrum("get").toHexString()
			eventId = $(this).data('id')
			eventName = $(this).html()
			if confirm("Are you sure you want to make " + eventName + " a premium event?")
				Bazaarboy.post 'admin/event/premium/', {id:eventId, color:color}, (response) ->
					if response.status is 'OK'
						window.location.href = response.redirect
					else
						alert response.message
					return
		$('.profile_login').on 'click', '.profile_choices a', (event) ->
			id = $(this).data('id')
			Bazaarboy.get 'admin/login/profile/', {id: id}, (response) ->
				if response.status is 'OK'
					Bazaarboy.redirect 'index'
				else
					alert response.message
				return
			return
		$('.profile_login .input_container input[name=profile_name]').keyup (event) =>
			value = $('.profile_login .input_container input[name=profile_name]').val()
			if value
				@searchProfiles(value)
			else
				$('.profile_login .profile_choices').empty()
			return
		$('div.event_export .input_container input[name=event_name]').keyup (event) =>
			value = $('div.event_export .input_container input[name=event_name]').val()
			if value
				@searchEvents(value)
			else
				$('div.event_export .event_choices').empty()
			return
		return

Bazaarboy.admin.login.init()