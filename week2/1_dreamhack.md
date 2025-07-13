## 목차
* [XSS](#xss)
    - [xss-1](#xss-1)
    - [xss-2](#xss-2)
* [CSRF](#csrf)
    - [csrf-1](#csrf-1)
    - [csrf-2](#csrf-2)

## XSS

### xss-1
* /vuln 페이지에서는 입력받은 param을 그대로 return함
	-> HTML 태그 입력시 그대로 parse되어 실행될 수 있음
	-> 이 과정에서, script 태그 안의 코드가 그대로 실행될 수 있음
	-> payload: `<img src="http://127.0.0.1:8000/admin/notice_flag?userid=admin"/>`

* /memo 페이지에서는 param으로 들어온 memo를 그대로 global memo_text에 추가함

* /flag 페이지에서는 cookie에 FLAG를 그대로 넣은 채로 `127.0.0.1:8000/vuln?param=...`에 요청을 보냄
	-> 127.0.0.1:8000에서 /memo?memo= 뒤에 document.cookie를 붙여 보낸다면 이후 /memo에서 쿠키의 FLAG를 볼 수 있음
	-> 127.0.0.1:8000/vuln 페이지에서 해당 페이지로 리다이렉트 시켜주면 됨.
	-> window.location.href를 설정해주면 해당 페이지로 리다이렉트됨.
	-> payload: `<script>window.location.href="http://127.0.0.1:8000/memo?memo="+document.cookie;</script>`
		-> href 설정시 protocol(`http://`) 넣어주는 것 까먹지 말자!

### xss-2
* 이 문제는 xss-1과 비슷하지만, /vuln 페이지가 입력받은 내용을 그대로 리턴하는 대신 html에 삽입해 렌더링 후 보여준다는 차이가 있었습니다.
* 이 경우, xss-1에서와 같이 script 태그를 그대로 사용하면 실행 순서때문에 삽입한 스크립트가 실행되지 않는 문제가 있습니다.
* 이를 우회하기 위해, 실행 순서가 후순위인 img 태그의 onerror 이벤트를 사용했습니다.
    - img 태그의 src에 invalid한 값을 넣어두면, img태그를 로드할 때 error가 발생하여 onerror Event Handler가 호출됩니다.
* 최종적인 Payload는 `<img src="invalid" onerror="window.location.href='http://127.0.0.1:8000/memo?memo='+document.cookie;"></img>`입니다.
    - 해당 payload를 /flag에 입력 후 /memo에 flag={flag}가 정상적으로 추가된 것을 확인하였습니다.

## CSRF

### csrf-1
* GET /admin/notice_flag 요청시 global memo_text에 flag가 추가됨
	-> 어떻게든 /admin/notice_flag에 요청을 날린다면 /memo에 접근해 flag를 얻을 수 있음
	-> 하지만, /admin/notice_flag는 127.0.0.1:8000/admin/notice_flag?userid=admin 로만 접근할 수 있음.

* /vuln에서는 입력받은 param을 그대로 return함
	-> HTML 태그 입력시 그대로 parse되어 실행될 수 있음
	-> 하지만, 입력값을 전부 소문자로 바꿔 `frame`, `script`, `on`을 `*`로 filter한 후 parse함.
	-> img 태그는 자동으로 src 속성에 지정된 주소로 GET 요청을 보냄
	-> 이를 통해 문제에서 요구하는 GET /admin/notice_flag를 구현할 수 있음.
	-> payload: `<img src="http://127.0.0.1:8000/admin/notice_flag?userid=admin"/>`

* /flag에서는 `127.0.0.1:8000/vuln?param={param}`에 요청을 보낼 수 있음
	-> 이 페이지를 통해 나의 로컬이 아닌 서버의 로컬에서 위 페이로드를 실행할 수 있음

### csrf-2
