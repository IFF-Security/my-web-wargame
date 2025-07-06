[[ < 이전 페이지로 ]](./index.md)

# 기타 개념 설명

## 목차
- [Parameter Tampering Attack](#parameter-tampering-attack)
- [IDOR](#idor)
- [Domain/DNS](#domaindns)
    - [DNS Rebinding](#dns-rebinding)
- [URI/URL](#uriurl)
- [Host Split Attack](#host-split-attack)
- [Robots.txt](#robotstxt)

## Parameter Tampering Attack

* 쿼리스트링, 숨은 폼 필드, 쿠키 등을 악의적으로 조작해 내부 로직 혹은 데이터를 변조하거나 탈취하는 기법
* 공격 방법
    - 공격자가 개발자 도구, 프록시 등을 통해 파라미터를 직접 변조
    - 중간자 기법: 공격자가 패킷을 가로채 파라미터를 조작한 후 서버로 전송
    - Burp Suite 등 자동화 도구를 사용해 파라미터 변조 자동화
* ex) \<input type="hidden" name="price" value="100"\>
    - 공격자가 value를 1로 수정하여 결제 금액을 축소할 수 있음
* 방어법
    - 서버측 무결성 검증
    - 중요 파라미터는 암호화하여 변조 탐지
    - 중요 로직은 클라이언트->서버 뿐만 아니라 서버->내부DB에서도 교차검증

## IDOR

* Request 정보를 조작해 수직/수평적 권한 상승을 발생시켜 타 사용자 정보에 접근하거나 기존 권한으로 사용 불가능한 기능을 이용하는 기법
* 공격 예시
    - 수평적 권한상승 (ID=1234인 사용자가 ID=1235인 사용자를 공격)
        - GET /mypage/info?id=1235 -> 리소스 무단 접근
        - PUT /mypage/info?id=1235 ... phone=010-1234-5678 -> 리소스 임의 변경
    - 수직적 권한 상승 (ID=1234인 사용자가 admin 권한 사용)
        - GET /admin/dashboard -> 관리자 대시보드에 직접 접근
        - DELETE /user/member/1235 ... Cookie: role=admin -> 임의 계정 삭제
* 방어법
    - 서버가 발급한 세션을 통해 리소스 접근 권한을 체크
    - 실제 사용자가 요청 내용에 대한 권한을 가지는지 서버에서 확인

## Domain/DNS

* 네트워크 통신에는 기본적으로 IP 주소가 필요하다.
    - 하지만 IP는 사람이 이해하고 기억하기 어렵다.
    - 때문에 각 IP에 부여한 이름이 도메인이다.
* DNS(Domain Name Server)는 도메인에 연결된 서버의 IP주소를 찾아주는 역할을 한다.

### DNS Rebinding

* 공격자가 제어하는 DNS 서버를 통해 피해자의 브라우저가 공격자의 도메인을 내부망 IP로 연결되도록 유도함으로써 브라우저의 SOP를 우회하고 내부망에 접근하는 기법.
* 동작 원리
    - 초기 DNS 응답
        - 공격자 도메인의 A 레코드를 공용IP로 지정하고, TTL을 매우 짧게 지정
        - 피해자가 해당 도메인에 접속하면 악성 스크립트가 삽입된 공격자의 서버에 접근
    - TTL 만료 후 Rebinding
        - TTL이 만료되면 브라우저가 동일한 도메인에 대해 다시 DNS 질의 수행
        - 이 때 공격자가 A 레코드를 내부망 IP로 변경하여 응답
        - 브라우저는 도메인 이름 같으면 동일 출처로 판단해 내부망 IP로 요청 허용
* 방어법
    - DNS 레코드 필터링
        - 내부망 IP에 대한 외부 도메인 응답을 사내 DNS 서버에서 차단
    - HTTPS 강제 적용
        - 내부 자원에 유효한 인증서가 없을 경우, DNS 리바인딩 후에도 인증서 검증 실패로 연결 차단

## URI/URL

* URI: Uniform Resource Identifier
    - 자원 자체를 식별하는 방법
* URL: Uniform Resource Locator
    - 자원의 위치를 알려주기 위한 방법
    - URL이 URI에 포함되는 구조이다.
* 예시: `https://www.example.com/post.html?id=1234`
    - 위 예시에서 ?id=1234는 자원의 위치가 아니라 자원을 식별하는 부분이다.
    - 따라서 URL은 `https://.../post.html`까지, 그리고 URI는 `https://.../post.html?id=1234`까지를 의미한다.

## URL Encoding

* URL에는 영숫자와 일부 특수문자(-, _, ., ~)만 사용할 수 있다.
* 하지만 자료명에 한글 등 허용되지 않은 문자가 포함될 수 있다.
* 이러한 자료 또한 접근할 수 있게 이름을 적절히 변환해 주는 것이 URL Encoding이다.
* 허용되지 않은 문자를 모두 16진수 유니코드로 변환 후, 2자리씩 끊어 앞에 %를 붙여주는 형식이다.

## Host Split Attack
[#1](https://blog.rubiya.kr/index.php/2019/08/13/host-split-attack/)

* 브라우저는 URL에서 비슷해보이는 유니코드를 표준 형태로 바꾼 다음 해석을 시작한다. 이를 Normalization이라고 한다.
* 이 때 `¼`과 같은 문자는 `1/4`로 표준화되는데, 이렇게 한 문자가 두 개 이상의 문자로 "분할"이 가능하다.
* 만약 공격자가 도메인에 분할 가능한 문자를 넣는다면, 브라우저는 정규화를 먼저 수행한다.
    - 예를 들어, 공격자의 도메인이 `evil.c¼.com`이라면, 정규화 이후에는 `evil.c1/4.com`이 된다.
    - 서버나 라이브러리는 호스트의 허용 여부를 정상 도메인 (`evil.c1`)에 대해서만 체크하고 `/4.com` 등의 경로는 체크하지 않는 경우가 많다.
    - 이 기법을 통해 Open Redirect, SSRF 등의 취약점 방어를 우회할 수 있다.

## Robots.txt

* robots.txt는 크롤러가 사이트에서 엑세스할 수 있는 URL을 알려준다.
* robots.txt는 요청으로 인한 과부하를 방지하기 위한 파일이다.
    - 페이지가 구글 등 검색엔진에 표시되는 것을 방지하기 위한 메커니즘이 아니다.
* 주의사항
    - robots.txt는 크롤러의 동작을 강제하는 지침이 아니다.
        - Googlebot 등 잘 제작된 크롤러는 이 지침을 준수하지만, 그렇지 않는 크롤러도 있다.
    - 크롤러마다 지침을 다르게 해석하는 경우도 있으며, 특정 지침을 이해하지 못하는 크롤러도 있다.
    - robots.txt에서 허용되지 않았지만 다른 곳에서 연결된 페이지는 색인이 생성될 수 있다.
* 구성요소 (Google 기준)
    - robots.txt는 1개 이상의 `그룹`과 0개 이상의 `사이트맵`으로 이루어진다.
    - 각 그룹은 User-Agent, Allow, Disallow로 구성된다.
        - User-Agent: 그룹의 지침을 적용할 에이전트를 지정한다.
            - 그룹별 1개 이상 작성
        - Allow: 지정한 에이전트에게 크롤링을 허가할 페이지를 지정한다.
            - Disallow와 합쳐서 그룹별 1개 이상 작성
        - Disallow: 지정한 에이전트에게 크롤링을 금지할 페이지를 지정한다.
            - Allow와 합쳐서 그룹별 1개 이상 작성
    - 사이트맵은 Sitemap으로 구성된다.
        - Sitemap: 사이트의 사이트맵의 위치를 지정한다.
