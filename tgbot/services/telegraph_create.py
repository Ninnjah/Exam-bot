import codecs

from telegraph import Telegraph

from tgbot.services.my_rtf_to_text import rtf_to_text


def get_rtf_text(filename: str) -> str:
    """Read RTF file and converts it to text"""
    with codecs.open(filename, "r", "cp1251") as f:
        rtf = f.read()

    text = rtf_to_text(rtf, encoding="cp1251")
    
    return text


def create_page(filename: str, title: str) -> str:
    """Creates telegraph page with text from RTF file"""
    telegraph = Telegraph()
    telegraph.create_account(short_name="PolyER Exam bot")

    text = get_rtf_text(filename).split('\n')

    html = f"<b>{text.pop(0)}</b>"
    for i in text:
        html += f"<p>{i}</p>"

    url = telegraph.create_page(title=title, html_content=html).get("url")
    return url
