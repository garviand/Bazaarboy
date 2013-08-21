from bs4 import BeautifulSoup

redactorAllowedTags = [
    'code', 'span', 'div', 'label', 'a', 'br', 'p', 'b', 'i', 'del', 'strike', 
    'u', 'img', 'video', 'audio', 'iframe', 'object', 'embed', 'param', 
    'blockquote', 'mark', 'cite', 'small', 'ul', 'ol', 'li', 'hr', 'dl', 'dt', 
    'dd', 'sup', 'sub', 'big', 'pre', 'code', 'figure', 'figcaption', 'strong', 
    'em', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'h1', 'h2', 
    'h3', 'h4', 'h5', 'h6'
]
redactorAllowedAttrs = [
    'height', 'width', 'style', 'src', 'href', 'target', 'srolling', 
    'frameborder', 'allowfullscreen', 'webkitAllowFullScreen', 
    'mozallowfullscreen'
]
iframeAllowedDomains = [
    'www.youtube.com', 'player.vimeo.com', 'w.soundcloud.com'
]

def sanitize_redactor_input(string):
    """
    Sanitize the input from redactor
    """
    string = unicode(string)
    string = string.replace('<br>', '<br />')
    while True:
        soup = BeautifulSoup(string)
        removed = False
        for tag in soup.findAll(True):
            if tag.name not in redactorAllowedTags:
                tag.extract()
                removed = True
            else:
                shouldExtractTag = False
                for attr, value in tag.attrs.items():
                    if attr not in redactorAllowedAttrs:
                        del tag[attr]
                    elif attr == 'src' and tag.name == 'iframe':
                        domain = value[value.index('//') + 2:].split('/')[0]
                        if domain not in iframeAllowedDomains:
                            shouldExtractTag = True
                            break
                if shouldExtractTag:
                    tag.extract()
                    removed = True
        string = unicode(soup)
        if removed:
            continue
        return string