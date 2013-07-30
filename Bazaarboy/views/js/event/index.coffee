Bazaarboy.event.index = 
    init: () ->
        $(document).ready () ->
            $('div.description div.editable').redactor
                buttons: [
                    'formatting','bold', 'italic', 'deleted', 'fontcolor', 
                    'alignment', '|',
                    'unorderedlist', 'orderedlist', 'outdent', 'indent', '|',
                    'image', 'video', 'link', '|',
                    'horizontalrule'
                ]
                imageUpload: rootUrl
            $('div.description div.controls a.save').click () ->
                description = $('div.description div.editable').redactor('get')
                console.log description
                return
            return
        return