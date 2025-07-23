## 목차
* [Non-persistant XSS (Reflected XSS)](#non-persistant-xss-reflected-xss)
* [Persistant XSS (Stored XSS)](#persistant-xss-stored-xss)
* [DOM XSS](#dom-xss)
* [기타](#기타)
    * [UXSS (Universal XSS)](#uxss-universal-xss)
    * [Blind XSS](#blind-xss)
    * [mXSS (Mutation XSS)](#mxss-mutaion-xss)
    * [SSXSS (Server-Side XSS)](#ssxss-server-side-xss)

## Non-persistant XSS (Reflected XSS)
* 직역하면 "비지속적인 XSS", "반사된 XSS"
* 이름 그대로 지속적이지 않은 XSS
    - 검색, 조회 등 사용자 입력으로 받은 데이*터가 페이지에 **반사**되어 노출되는 경우 사용
* 예시 페이로드
    - `request.get(base + '/vuln?content=<script>alert("XSS!");</script>')`
*
## Persistant XSS (Stored XSS)
* 직역하면 "지속적인 XSS", "저장된 XSS"
* 이름 그대로 사용자에게 지속적인 피해를 줄 수 있는 XSS
    - 프로필 저장, 게시글/댓글 작성 등 서버에 데이터를 올리고 사용자가 데이터를 확인할 수 있는 경우 사용
* 예시 페이로드
    - Save: `request.post(base + '/vuln', json.stringify({ name: '<script>alert("XSS!");</script>' }))`
    - Trigger: `request.get(base + '/vuln')`

## DOM XSS
* Reflected, Stored XSS는 입력한 값이 페이지에 직접 반영되는 경우 사용한다.
* 반면, DOM XSS는 JS 등 DOM 내부 처리 중 스크립트가 실행될 수 있는 경우 사용한다.
* 예시 페이로드
    - `request.get(base + '/vuln#<script>alert("XSS!");</script>')`
    - Reflected XSS와 페이로드가 매우 비슷하다.
    - 그러나, 실행 시점 및 위치 등에서 차이를 보인다.

## 기타 

### UXSS (Universal XSS)
* 불특정한 사이트에서 발생하는 XSS
* 주로 모바일 앱에서 발생하며, WebView 자체에서 발생하는 XSS 등이 있음

### Blind XSS
* 고객센터나 문의 페이지 등 공격자가 실행 여부를 즉시 확인할 수 없는 XSS
* Blind XSS가 어떤 페이지에서 실행되었는지 등의 자세한 실행정보에 대한 파악을 하기 위해 XSSHunter 등의 도구를 사용했다고 함.
    - 현재는 Deprecated됨.

### mXSS (Mutaion XSS)
* HTML Parser의 느슨한 검사를 이용한 XSS
* 구문상 non-script 영역으로 처리하지만 실제로는 scripting이 가능한 형태

### SSXSS (Server-Side XSS)
* 일반적인 XSS와 달리 서버에서 실행되는 XSS
* 주로 서버에서 Headless browser를 이용해 페이지에 접근할 때 발생
* XSS와 유사하지만, Server-Side에서 작동하기에 LFI, SSRF 등의 공격이 가능함
