$(document).ready ->

    $("form[name=login]").submit (event) ->
        event.preventDefault()
        return false

    $("form[name=register]").submit (event) ->
        event.preventDefault()
        return false