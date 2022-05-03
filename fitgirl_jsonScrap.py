import time
import json
import random
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime


def repackReleaseDate(_date):
    return datetime.strptime(_date, "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y")


def htmlConvert(_html):
    return BeautifulSoup(_html, "html.parser").get_text()


def isRepack(data):
    return '#' in htmlConvert(data['content']['rendered'])


def writeFitgirlJson(data):
    Path("FitGirlData.json").write_text(json.dumps(data, indent="\t"))


def getDetail(soup):
    children = soup.select_one("p").children
    a = [child for child in children if child.text]

    gets = ['genres', 'compan', 'language', 'original', 'repack', 'magnet:?',
            "https://cs.rin.ru/forum/viewtopic.php?", "description", "selective"]
    details = []

    if gets[0] in a[0].get_text().lower():
        details.append(a[1].get_text())
    else:
        details.append("")

    c = 1
    for index, i in enumerate(a):
        if gets[c] in i.get_text().lower():
            details.append(a[index + 1].get_text())
            c += 1
        if c == 5:
            break

    d = soup.select_one("li")
    if d:
        for f in d.select("a"):
            if f.get("href") and gets[5] in f.get("href"):
                details.append(f.get("href"))
                break
        else:
            details.append("")
    else:
        for f in soup.select("p")[1].select("a"):
            if gets[5] in f.get("href"):
                details.append(f.get("href"))
                break
        else:
            details.append("")

    for i in soup.select("p"):
        if i.a and i.a.get("href") and gets[6] in i.a.get("href"):
            details.append(i.a.get("href"))
            break
    else:
        details.append("")

    details.append("")
    details.append("")
    if soup.select("div"):
        for div in soup.select("div"):
            if div.select("div"):
                if gets[7] in div.select("div")[0].get_text().lower():
                    details[7] = div.select("div")[1].get_text()
                elif gets[8] in div.select("div")[0].get_text().lower():
                    details[8] = div.select("div")[1].get_text()

    for i in soup.select("ul"):
        t = i.get_text().lower()
        if "based" in t and "lossless" in t or "install" in t:
            details.append(i.get_text())
            break
    else:
        details.append("")

    gameName = list(soup.select_one("h3").strong.children)
    details.append(gameName[0].get_text())
    if len(gameName) > 1:
        details.append(gameName[1].get_text())
    else:
        details.append("")

    return details


def simplify(data):
    soup = BeautifulSoup(data['content']['rendered'], "html.parser")
    detail = getDetail(soup)
    return {
        "id": 0,
        "postId": data['id'],
        "repackId": soup.select_one("h3").span.get_text(),
        "repackTitle": htmlConvert(data['title']['rendered']),
        "repackReleaseDate": repackReleaseDate(data['date']).upper(),
        "gameTitle": detail[10],
        "gameVersion": detail[11],
        "genres/Tags": detail[0],
        "companies": detail[1],
        "languages": detail[2],
        "gameSize": detail[3],
        "repackSize": detail[4],
        "magnetUrl": detail[5],
        "discussionUrl": detail[6],
        "repackUrl": data['link'],
        "repackFeatures": detail[9],
        "gameDescription": detail[7],
        "selectiveDownload": detail[8],
    }


def downloadJson(post):
    response = requests.get("https://fitgirl-repacks.site/wp-json/wp/v2/posts/" + str(post))
    data = json.loads(response.text)
    if not data.get('data', 0) and isRepack(data):
        Path("json/" + str(post) + ".json").write_text(json.dumps(simplify(data), indent="\t"))
        print(str(post) + ".json downloaded")
    else:
        print(post)


if __name__ == "__main__":
    start_time = time.time()

    start, end = 0, 26071
    for post in range(start, end + 1):
        downloadJson(post)

    print(f"\n\nTime taken {time.time() - start_time} sec")
