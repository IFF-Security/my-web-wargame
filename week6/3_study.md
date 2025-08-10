## 목차
- [목차](#목차)
- [SSRF](#ssrf)
- [SSTI](#ssti)

## SSRF
* SSRF (Server Side Request Forgery)
  * 직역하면, 서버측 요청 위조
* 서버에서 다른 서버로 보내는 요청을 위조해 공격자가 서버의 취약한 부분에 액세스하는 것
* CSRF와 원리는 같지만, CSRF는 피해자가 다른 (공격자의) 사이트에 접속해 그 사이트가 대상 서버에 요청을 보내는 반면, SSRF는 공격자가 웹 요청을 수행하는 서버에 접근해 잘못된 요청을 보내게 한다는 차이가 있다.
  * 도식화하자면, 다음과 같다.
  * CSRF: 피해자 -> (공격자의 사이트) -> (취약 서버)
  * SSRF: 공격자 -> (취약 서버) -> (피해 서버 ; 주로 취약 서버와 동일)
* DreamHack 문제 복기
  * 5주차의 web-ssrf 문제는 /img_viewer 라우트에서 입력받은 URL 그대로 요청을 보내 SSRF 취약점이 발생한다.
  * 해당 URL에 localhost의 검열을 피해 1500~1800번 포트에 한 번씩 POST 요청을 보내고, 그 중 정상적인 응답을 한 서버에서 flag.txt 폴더에 접근하는 문제였다.

## SSTI
* SSTI (Server Side Template Injection)
  * 직역하면, 서버측 템플릿 주입
  * 템플릿 (Template)
    * DB/API 호출 결과, 사용자의 입력 등 상황에 따라 바뀌는 값을 미리 정의된 템플릿에 넣어 HTML을 완성해 클라이언트에 전달하는 역할
* 서버에서 입력 받은 값을 검증/Escaping 없이 템플릿 스트링에 넣을 때 발생하는 취약점
  * 예를 들어, Flask의 Jinja 엔진에서는 다음과 같은 상황에서 문제가 발생할 수 있다.
    ```py
    user_input = "{{ 7*7 }}" # MALCIOUS !!
    template = f"<div>{user_input}</div>"
    return render_template_string(template)
    ```
    * 해당 코드로 렌더링된 결과는 `<div>49</div>` 이다.
* DreamHack 문제 복기
  * 5주차의 simple-ssti 문제는 404페이지에서 Route를 그대로 template string에 삽입하여 SSTI 취약점이 발생한다.
  * `/{{ config }}` Route에 접근하려 하면 쉽게 플래그를 획득할 수 있었다.
