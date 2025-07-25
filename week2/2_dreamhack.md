## 목차
* [XSS](#xss)
    - [xss-1](#xss-1)
    - [xss-2](#xss-2)
* [CSRF](#csrf)
    - [csrf-1](#csrf-1)
    - [csrf-2](#csrf-2)

## XSS

### xss-1
* 해당 문제는 서버의 아래 코드에서 문제가 발생한다.
	```py
	@app.route("/vuln")
	def vuln():
		param = request.args.get("param", "")
		return param
	```
* 해당 코드는 Request의 파라미터로 들어온 값을 그대로 return한다.
	- 이 과정에서 HTML 태그가 포함되어있다면 그대로 렌더링된다.
	- 즉, 해당 Route에서 script 태그를 활용한 Reflected XSS가 가능하다.
* 정답 페이로드: `<script>window.location.href="http://127.0.0.1:8000/memo?memo="+document.cookie;</script>`

<details>
<summary>기존 서술, 문제 풀이 중점</summary>

* /vuln 페이지에서는 입력받은 param을 그대로 return함
	- HTML 태그 입력시 그대로 parse되어 실행될 수 있음
	- 이 과정에서, script 태그 안의 코드가 그대로 실행될 수 있음

* /memo 페이지에서는 param으로 들어온 memo를 그대로 global memo_text에 추가함

* /flag 페이지에서는 cookie에 FLAG를 그대로 넣은 채로 `127.0.0.1:8000/vuln?param=...`에 요청을 보냄
	- 127.0.0.1:8000에서 /memo?memo= 뒤에 document.cookie를 붙여 보낸다면 이후 /memo에서 쿠키의 FLAG를 볼 수 있음
	- 127.0.0.1:8000/vuln 페이지에서 해당 페이지로 리다이렉트 시켜주면 됨.
	- window.location.href를 설정해주면 해당 페이지로 리다이렉트됨.
	- payload: `<script>window.location.href="http://127.0.0.1:8000/memo?memo="+document.cookie;</script>`
		- href 설정시 protocol(`http://`) 넣어주는 것 까먹지 말자!
</details>

### xss-2
* 해당 문제는 vuln.html의 아래 부분에서 문제가 발생한다.
	```html
	<script>
		var x = new URLSearchParams(location.search);
		document.getElementById('vuln').innerHTML = x.get('param');
	</script>
	```
* 해당 스크립트는 Request의 파라미터로 들어온 값을 오브젝트의 innerHTML에 그대로 넣어준다.
	- 이 경우 xss1과 같은 script 태그 기반의 XSS는 활용이 불가능하다.
		- 리렌더링시 처음 문서를 파싱할 때 만난 스크립트가 아니므로 다시 실행하지 않기 때문이다.
		- cf) 런타임에 생성된 script태그가 실행되려면 아래의 명시적 삽입 절차를 거쳐야 한다.
			```js
			const script = document.createElement('script');
			
			script.src = '/* src */';
			// or...
			script.text = '/* code */';
			
			parentNode.appendChild(script);
			```
	- 이러한 특성으로 인해 xss1과 같이 script 태그를 직접 삽입하는 방식은 작동하지 않는다.
	- 하지만 innerHTML을 직접 수정하기 때문에 DOM XSS 공격이 가능하다.
		- 일례로, img태그 등 외부 리소스가 연결된 오브젝트를 생성하거나 수정하면 브라우저는 즉시 해당 URL로 네트워크 요청을 보낸다.
		- 이 과정에서, 이미지 요청 실패시 실행되는 이벤트인 `onerror`를 이용해 임의의 스크립트를 실행하는 것이 가능하다.
* 정답 페이로드: `<img src="invalid" onerror="window.location.href='http://127.0.0.1:8000/memo?memo='+document.cookie;" />`

<details>
<summary>기존 서술, 문제 풀이 중점</summary>

* 이 문제는 xss-1과 비슷하지만, /vuln 페이지가 입력받은 내용을 그대로 리턴하는 대신 html에 삽입해 렌더링 후 보여준다는 차이가 있었습니다.

* 이 경우, xss-1에서와 같이 script 태그를 그대로 사용하면 실행 순서때문에 삽입한 스크립트가 실행되지 않는 문제가 있습니다.

* 이를 우회하기 위해, 실행 순서가 후순위인 img 태그의 onerror 이벤트를 사용했습니다.
	- img 태그의 src에 invalid한 값을 넣어두면, img태그를 로드할 때 error가 발생하여 onerror Event Handler가 호출됩니다.

* 최종적인 Payload는 `<img src="invalid" onerror="window.location.href='http://127.0.0.1:8000/memo?memo='+document.cookie;"></img>`입니다.
	- 해당 payload를 /flag에 입력 후 /memo에 flag={flag}가 정상적으로 추가된 것을 확인하였습니다.
</details>

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
* Root 페이지에서는 navigator와 함께 안내 메시지를 확인할 수 있음.
	- admin으로 로그인시 해당 안내메시지에서 flag를 확인할 수 있음.

* /vuln 페이지에서는 csrf-1과 동일한 역할을 수행함.
	- 입력받은 param을 그대로 return함
	- HTML 태그 입력시 그대로 parse되어 실행될 수 있음
	- 하지만, 입력값을 전부 소문자로 바꿔 frame, script, on을 *로 filter한 후 parse함.
	- img 태그는 자동으로 src 속성에 지정된 주소로 GET 요청을 보냄

* /flag 페이지에서는 아래 동작을 수행함.
	- admin의 session_id를 만들어서 cookie에 추가
	- `127.0.0.1:8000/vuln?param=...`에 요청을 보내고, 성공 여부를 보여줌.

* /login 페이지에서는 입력받은 pw를 서버 파일의 users dict에서 가져온 pw와 비교해 일치하면 로그인시켜줌
	- guest는 pw=guest로 바로 로그인할 수 있음.
	- 하지만, admin은 비밀번호가 FLAG라서 바로 로그인할 수 없음. (FLAG를 아직 모름)

* /change_password 페이지에서는 cookie에서 session_id를 확인하고, users에서 pw를 업데이트해줌.
	- 이 요청은 GET요청으로도 진행됨.
	- 따라서, xss-2에서 사용한 img태그를 사용한 공격이 가능함.
	- payload: `<img src="http://127.0.0.1:8000/change_password?pw=1234"/>`
	- /flag 페이지에서 payload를 입력하면 POST 요청 처리 부분에서 session_id를 만든 후 요청을 보냄
	- 따라서 cookie 탈취를 따로 고민할 필요 없음.

* 최종 정답
	- /flag 페이지 payload: `<img src="http://127.0.0.1:8000/change_password?pw=1234"/>`
	- 이후 / (index) 접근으로 flag 획득 가능
