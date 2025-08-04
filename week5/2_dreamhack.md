## 목차
- [목차](#목차)
- [web-ssrf](#web-ssrf)
- [simple-ssti](#simple-ssti)
- [chocoshop](#chocoshop)

## web-ssrf
* 서버 파일 분석
  * app.py의 17번 줄에서, 플래그는 서버파일과 동일한 경로의 flag.txt 파일에 저장되어있음을 확인할 수 있다.
  * app.py의 /img_viewer 라우트에서, 사용자에게 입력받은 url을 간단한 체크만 하고 해당 url에 get 요청을 하는 것을 확인할 수 있다.
    * 해당 부분에서 SSRF(Server Side Request Forgery) 공격이 가능함을 확인할 수 있다.
      * 하지만 요청을 보낼 도메인에서는 localhost와 127.0.0.1를 검열하기에, 서버로 요청을 보내기 위해서는 이를 우회할 필요가 있다.
    * 요청한 url에서 받은 이미지, 혹은 error.png를 로드해 base64로 인코딩하여 img_viewer.html 파일에 그대로 img 태그로 렌더링한다.
      * 이를 통해, SSRF 공격이 제대로 실행되었다면 태그의 src 속성 중 `data:image/png;base64, ` 뒤에 나오는 부분을 base64로 디코딩하여 플래그를 얻을 수 있음을 알 수 있다.
  * app.py의 48번 줄부터, 로컬호스트의 특정 포트에서 디렉터리를 HTTP로 매핑하는 서버를 열어두는 것을 확인할 수 있다.
    * 해당 서버의 포트는 1500번에서 1800번 사이의 랜덤한 포트로 열린다.
    * 해당 서버의 포트를 알 수 있다면, 해당 서버에 접근하여 flag.txt 파일에 접근할 수 있다.
* HTTP 요청 관련 배경지식
  * HTTP 요청시, 도메인/IP 부분에 정수를 적으면 해당 정수를 IP로 해석한다.
    * 임의의 16진수 A~H에 대해, `0xABCDEFGH`를 `(0xAB).(0xCD).(0xEF).(0xGH)`로 해석한다.
  * 따라서, `127.0.0.1:8000`과 `0x7f000001:8000`은 동일한 주소를 나타낸다.
* 실제 Exploit 코드는 `2.1_web_ssrf.py` 참조.

## simple-ssti
* 서버 파일 분석
  * app.py의 404 handler 페이지에서, request.path를 그대로 h3 태그에 넣고 보여주는 것을 확인할 수 있다.
  * 해당 부분에서 SSTI(Server Side Template Injection) 공격이 가능함을 확인할 수 있다.
    * 검증을 위해 `/{{ 1 }}`에 접근을 시도하고, 정상적으로 URL에 `/1`만 있는 것을 확인했다.
* Flask 관련 배경지식
  * Flask는 내부적으로 config dictionary를 가지고 있으며, app의 멤버변수처럼 접근하고 수정하는 것 또한 가능하다.
    * 이에 따라 11번 줄은 `app.config["secret_key"] = FLAG`와 동일한 효과를 준다.
  * 또한, render시 config 객체가 자동으로 넘어간다.
    * 때문에 `{{ config }}`을 통해 flask의 config dictionary에 접근할 수 있다.
* 최종 풀이
  * `/{{ config["SECRET_KEY"] }}`에 접근해 Flag를 얻는다

## chocoshop
