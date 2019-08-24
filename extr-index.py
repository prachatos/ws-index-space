import urllib.request
from urllib.error import HTTPError
import configparser, re
import requests

if __name__ == '__main__':

    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini', encoding='utf8')
    try:
        LANG_CODE = config_parser.get('wiki', 'lang')
    except Exception:
        LANG_CODE = 'en'
    i = 0

    links = []
    while True:
        page = requests.get("https://" + LANG_CODE + ".wikisource.org/w/index.php?title=Special:IndexPages&limit=5000&offset=" + str(i) + \
                            "&key=&order=")
        print(page.content)
        from lxml import html
        content = html.fromstring(page.content)
        links_found = 0
        for item in content.xpath("//div"):
            if "prp-indexpages-row" in item.classes:
                links_found += 1
                link = item.findall('.//a')[0].get('href')
                name = link.split('/')[::-1][0]
                links.append((name, "https://" + LANG_CODE + ".wikisource.org/w/index.php?title=" + name + "&action=raw"))
        if links_found == 0:
            break
        i += 5000

    try:
        page = requests.get(links[0][1])
        print(page.content)
        page.encoding = 'utf-8'
        page_content = str(page.content).split('|', 1)[1]
        headings = re.sub(r"(\|Remarks).*(\|Notes)", r'\1=\n\2', str(page.content)).split('|')
        headings.remove(headings[0])
        count = 0
        s = ""
        for heading in headings:
            prop, val = heading.split('=', 1)
            s += prop + "\t"
            print(prop)
        print(s[:-1], file=open(LANG_CODE + "-ws.tsv", "w+"))
    except Exception:
        pass
    import codecs
    from urllib.parse import unquote
    import re

    for y, l in links:
        page = requests.get(l)
        page.encoding = 'utf-8'
        page_content = str(page.content).split('|', 1)[1]
        headings = re.sub(r"(\|Remarks).*(\|Notes)", r'\1=\2', str(page.content))
        headings = re.sub(r"(\|Pages).*(\|Volumes)", r'\1=\2', headings)
        # print(headings)
        headings = headings.split('=')
        # print(headings)
        headings.remove(headings[0])
        s = unquote(y) + "\t" + "https://" + LANG_CODE + ".wikisource.org/wiki/" + unquote(y) + "\t"
        for heading in headings:
            try:
                val, prop = heading.split('|', 1)
            except Exception:
                val = heading
            val = val.replace("}}", "")
            val = val.replace("\\n", "")
            s += val + "\t"
        # print(s)
        with codecs.open(LANG_CODE + "-ws.tsv", "a+", "utf-8-sig") as temp:
            temp.write(bytes(s, 'utf-8').decode('unicode_escape').encode('latin-1').decode('utf8') + "\n")
