[[ < 이전 페이지로 ]](./index.md)

# HTTP 프로토콜

## 목차
- [HTTP Request/Response](#http-requestresponse)
    - [GET과 POST의 차이](#get과-post의-차이)
    - [Header 종류](#header-종류)
- [Cookie](#cookie)
    - [Cookie Property](#cookie-property)
    - [크롬에서 SameSite=Lax로 쿠키 기본 정책이 바뀐 이유](#크롬에서-samesitelax로-쿠키-기본-정책이-바뀐-이유)
- [Session](#session)
    - [Session vs Cookie](#session-vs-cookie)
    - [HTTP Session Hijacking](#http-session-hijacking)

## HTTP Request/Response

* HTTP는 기본적으로 클라이언트와 서버 사이의 통신 프로토콜이다.
* 여기서 클라이언트가 서버에게 전송하는 메시지를 Request, 서버가 클라이언트에게 응답으로 전송하는 메시지를 Response라고 한다.

### GET과 POST의 차이

* HTTP Request에는 서버가 수행해야 할 동작을 지칭하는 메서드가 여러 종류 있다.
* 그 중 가장 많이 쓰이는 것이 GET과 POST인데, 둘은 각각 아래와 같은 특징이 있다.

#### GET: 리소스 조회
* 서버에 리소스의 조회를 요청하는 메서드이다.
* 해당 메서드는 기본적으로 "조회"만 하기 때문에, 해당 메서드만 연속으로 여러번 사용해도 리소스는 변하지 않는다.
    - 이런 성질을 **멱등성** 이라고 한다.
    - 이런 성질을 기반으로 GET Request는 Caching 기능을 제공한다.
* 서버에 데이터를 전달하는 경우 "쿼리스트링"을 통해 전달한다.
    - 이는 URL의 맨 뒤에 `?(param1)=(value1)&...`의 형식으로 전달된다.
    - 이 방식은 클라이언트에게 전달하는 데이터가 그대로 노출되므로 주의가 필요하다.

#### POST: 데이터 추가/등록
* 서버에 새로운 데이터의 추가를 요청하는 메서드이다.
* 데이터를 메세지 바디에 쿼리 파라미터 형식으로 전달한다.
    - 쿼리 파라미터는 key-value pair로 구성된다.
    - 이는 GET 방식과 비교할 때 데이터가 외부로 노출되지 않으므로 상대적으로 안전하다.
    - POST Request로도 데이터를 제공하는 경우가 있으나, GET Request와 달리 멱등성을 가지지 않는다.
    - 또한 이 때문에 Caching 기능도 제공되지 않아 GET Request보다 조회 속도가 느리다.

### Header 종류
* Authorization: 유저 에이전트의 인증을 위한 헤더
* Cookie: 현재 저장되어있는 HTTP 쿠키
* Content-Type: 리소스의 미디어 타입
* Content-Length: 전송된 바디의 크기 (단위: 바이트)
* User-Agent: 요청하는 유저 에이전트의 애플리케이션과 운영체제 등을 식별할 수 있는 특성 문자열
* Origin: 요청이 시작된 서버의 이름

## Cookie

* 클라이언트와 서버 사이의 상태를 유지하고 관리하기 위한 작은 데이터 조각
* 서버와 브라우저 간의 연결을 유지하기 위한 식별데이터
* 주로 세션 관리, 개인화, 트래킹에 사용

### Cookie Property
* path: 요청하는 URL에 반드시 포함되어야 하는 경로
* domain: 쿠키가 저장되고 적용되는 서버의 호스트
* expires / max-age: 쿠키의 유효 기간 설정
    - expires={date}: {date}까지 유효, 그 이후 브라우저가 삭제
    - max-age={num}: {num}초 후까지 유효, 그 이후 브라우저가 삭제
    - 둘 다 설정된 경우 max-age가 우선권을 가짐.
* httpOnly: 설정된 경우 JS가 해당 쿠키에 접근하지 못하게 막음
* SameSite: 쿠키를 Cross-site Request와 함께 전달할지 설정
    - Strict: 동일 사이트에서의 요청에서만 전송됨, 타 사이트의 요청에서는 전송되지 않음.
    - Lax(기본값): 타 사이트의 GET 요청과 동일 사이트의 요청에서는 전송됨, 그 외 요청에서는 전송되지 않음.
        - fetch() API나 img, script, iframe 등 Subresources의 요청에서는 전송되지 않음
        - 유저의 클릭이나, document.location이나, form의 전송의 경우에는 전송됨.
    - None: 타 사이트의 모든 요청에서도 전송됨. 단, Secure 옵션이 강제됨.
* Secure: localhost 또는 https로의 요청에서만 전송됨.
    - 해당 옵션을 사용하면 중간자공격에 대한 보안성이 높아짐.

### 크롬에서 SameSite=Lax로 쿠키 기본 정책이 바뀐 이유
[#1](https://blog.rubiya.kr/index.php/2020/04/07/side-channel-attack-on-www/)
[#2](https://blog.rubiya.kr/index.php/2020/05/03/side-channel-attack-on-www-2/)

* iframe, script 등의 방식을 통한 쿠키 유출을 막기 위함.

## Session

* HTTP 프로토콜은 기본적으로 Connectionless함.
* 때문에 한 Request에서 이전 Request-Response의 결과를 기억하지 못함.
* 이를 해결하기 위해 개발된 기술.
* 클라이언트의 일련의 Request를 하나의 상태로 보고, 그를 일정하게 유지한다.

### Session vs Cookie
| 구분 | 세션 | 쿠키 |
| --- | --- | --- |
| 저장위치 | 서버 | 클라이언트 |
| 만료시점 | 브라우저 종료시 삭제 | 쿠키 저장시 설정 |
| 보안 | 안전 | 비교적 취약 |
| 속도 | 비교적 느림 | 빠름 |

### HTTP Session Hijacking

* 공격자가 유효한 Session ID를 탈취하여 서버 자원을 불법적으로 사용하는 행위
* 발생 원인
    - 유효하지 않거나 예측 가능한 Session ID 생성 알고리즘
    - 암호화되지 않은 전송
    - Session ID가 틀려도 조치가 없는 등 부적절한 오류 처리
* 방어법
    - 암호화된 통신 강제 (HTTPS/SSH)
    - Session ID 관리 강화
        - Session 만료 시간 설정
    - 로그아웃 기능
        - 명시적 로그아웃 시 Session Invalidate
        - 서버 측에서는 Session Store에서 즉시 제거
