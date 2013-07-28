from bs4 import BeautifulSoup

redactorAllowedTags = [
    'code', 'span', 'div', 'label', 'a', 'br', 'p', 'b', 'i', 'del', 'strike', 
    'u', 'img', 'video', 'audio', 'iframe', 'object', 'embed', 'param', 
    'blockquote', 'mark', 'cite', 'small', 'ul', 'ol', 'li', 'hr', 'dl', 'dt', 
    'dd', 'sup', 'sub', 'big', 'pre', 'code', 'figure', 'figcaption', 'strong', 
    'em', 'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'h1', 'h2', 'h3', 
    'h4', 'h5', 'h6'
]
redactorAllowedAttrs = []

def sanitize_redactor_input(string):
    """
    Sanitize the input from redactor
    """
    while True:
        soup = BeautifulSoup(string)
        removed = False
        for tag in soup.findAll(True):
            if tag.name not in redactorAllowedTags:
                tag.extract()
                removed = True
            else:
                for attr in tag.attrs.keys():
                    if attr not in redactorAllowedAttrs:
                        #del tag[attr]
                        pass
        string = unicode(soup)
        if removed:
            continue
        return string