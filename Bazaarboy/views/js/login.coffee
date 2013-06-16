$(document).ready ->
    $("form[name=login]").submit (event) ->
        event.preventDefault()
        return false
    return