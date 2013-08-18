Bazaarboy.profile.index = 
    init: () ->
        # Extend collapse animations
        collapseStates = [
            ['div#profile', [['margin-left', '63px', '96px']]]
            ['div#profile > div.title', [
                ['width', '750px', '876px']
                ['left', '-63px', '-96px']
            ]]
            ['div#profile > div.title div.text', [['left', '63px', '96px']]]
        ]
        $.merge(Bazaarboy.collapseStates, collapseStates)
        return

Bazaarboy.profile.index.init()