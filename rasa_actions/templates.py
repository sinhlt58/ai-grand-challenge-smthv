def Attachment_Buttons(text, buttons):
    _buttons = []
    for button in buttons:
        _buttons.append({
            "type": "postback",
            "title": button,
            "payload": button
        })

    template = {
        "attachment": {
            "type": "template",
            "payload": {
                "text": text,
                "template_type": "button",
                "buttons": _buttons,
            }
        }
    }

    return template

def Only_Text(text):
    template = {
        "text": text
    }

    return template

def Quick_Replies_Answers(quick_replies):
    text = ""
    _quick_replies = []
    for index, quick_reply in enumerate(quick_replies):
        text += "{}. {}\n".format(chr(65 + index), quick_reply)
        _quick_replies.append({
            "content_type": "text",
            "title": chr(65 + index),
            "payload": quick_reply,
        })

    template = {
        "text": text,
        "quick_replies": _quick_replies
    }

    return template

def Attachment_Link(type_url, url):
    template = {
        "attachment" : {
            "type" : type_url,
            "payload" : {
                "url" : url,
                "is_reusable" : False,
            }
        }
    }

    return template
