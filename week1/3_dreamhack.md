[[ < 이전 페이지로 ]](./index.md)

# DreamHack 문제 풀이

## 목차
- [command-injection-chatgpt](#1-command-injection-chatgpt)
    - [Command Injection](#command-injection)
    - [문제 풀이](#문제-풀이)
- [pathtraversal](#2-pathtraversal)
    - [Directory Listing](#directory-listing)
    - [Path Traversal](#path-traversal)
    - [문제 풀이](#문제-풀이-1)
- [file-download-1]
    - [File Upload/Download 취약점](#file-uploaddownload-취약점)
    - [문제 풀이](#문제-풀이-2)

## 1. command-injection-chatgpt

### Command Injection
* 입력값을 조작하여 시스템 명령어를 실행하는 기법
* SQL Injection이 DB Query를 조작한다면, Command Injection은 운영체제의 명령어를 조작한다는 비슷한 점이 있다.
* 주로 사용되는 특수문자
    - `;`(세미콜론): 하나의 라인에 입력된 명령어들을 성공 여부와 관계 없이 모두 실행한다.
    - `&`(앰퍼샌드): 앞의 명령어는 백그라운드에서 실행하고, 그의 성공 여부와 관계 없이 즉시 뒤의 명령어를 실행한다.
    - `&&`(더블 앰퍼샌드): 앞의 명령어가 실패하면 뒤의 명령어를 실행하지 않는다.
    - `|`(버티컬 바): 앞의 명령어의 Output을 뒤의 명령어의 Input으로 Stream 한다.
    - `||`(더블 버티컬 바): 앞의 명령어가 성공하면 뒤의 명령어를 실행하지 않는다.

### 문제 풀이
* https://dreamhack.io/wargame/challenges/768/
<details>
<summary>Writeup</summary>
<ul>
<li>해당 서버는 <code>host</code>를 입력받고 해당 host에 ping을 보내는 동작을 수행합니다.</li>
<li>이 과정에서 전처리 없이 입력받은 host를 <code>ping -c 3 </code> 뒤에 그대로 붙여 실행합니다.</li>
<li>여기에서 Command Injection 기법을 시도해볼 수 있으며, 저는 && 연산자를 사용해 이 기법을 사용했습니다.</li>
<li>다만 명령어의 실행에 5초의 timeout이 걸려있으며 timeout이 나면 실행 결과를 볼 수 없습니다.</li>
<li>때문에 가장 확실하고 가장 가까이에 있는 host인 <code>host3.dreamhack.games:{현재 port}</code>를 사용했습니다.</li>
<li><code>app.py</code>의 6번 줄에서 동일 위치에 flag.py가 있는 것을 확인할 수 있습니다.</li>
<li>리눅스 서버에서 실행될 것으로 예상하고 해당 파일을 읽기 위해 <code>cat</code> 명령어를 사용했습니다.</li>
<li>따라서 결과적으로 <code>host3.dreamhack.games:{port} && cat flag.py</code>를 입력하고 Ping! 버튼을 눌러 플래그를 획득할 수 있습니다.</li>
</ul>
</details>

## 2. pathtraversal

### Directory Listing
* 웹 서버가 디렉토리의 컨텐츠를 클라이언트에게 목록 형태도 보여주는 기능.
* 웹 브라우저에서 특정 디렉토리를 요청했을 때, 해당 디렉토리 안에 있는 파일 및 디렉토리 목록을 보여주도록 설정되어있다면 이를 Directory Listing이라고 한다.

### Path Traversal
* "디렉토리 조작"으로도 알려져있는 취약점
* 사용자로부터 경로(path) 형태의 입력값을 받아 서버의 파일에 접근할 수 있는 기법
* 경로와 관련된 특수문자(`../` 등)의 필터링 여부를 파악하는 것이 중요하다.
* 해당 특수문자가 실제 경로로 처리된 경우 상대경로를 이용해 서버의 파일에 접근을 시도할 수 있다.

### 문제 풀이
* https://dreamhack.io/wargame/challenges/12/
<details>
<summary>Writeup</summary>
<ul>
<li>위 문제는 <code>app.py</code> 파일만 제공하였으며, 실제 <code>get_info.html</code>은 제공되지 않았습니다.</li>
<li>우선 <code>/get_info</code>에 POST 요청을 주면 작성한 userid를 그대로 <code>/api/user/</code> 뒤에 붙여 GET 요청을 보내는 점을 이용해, userid에 먼저 <code>../flag</code>를 입력하고 버튼을 눌러보았습니다.</li>
<li>하지만 <code>get_info.html</code> 파일에서 View 버튼을 눌렀을 때 Form을 Submit하기 전에 userid를 전처리해 요청을 보내는 것을 확인할 수 있었습니다.</li>
    <ul><li>guest -> 0, admin -> 1, 그 외 -> undefined</li></ul>
<li>이를 해결하기 위해 userid에 <code>../flag</code>를 입력하고, View 버튼을 누르는 대신 개발자도구에서 form을 가져와 직접 <code>submit()</code> 함수를 호출했습니다.</li>
<li>이 방법은 전처리가 진행되지 않음을 확인했으며, 이를 통해 플래그를 확인할 수 있습니다.</li>
</ul>
</details>

## 3. file-download-1

### File Upload/Download 취약점
* Upload 취약점: 서버에 WebShell 등 악의적인 파일을 올려 원하는 기능을 실행할 수 있는 취약점
    - **Webshell**: Upload 취약점을 이용하여 시스템에 명령을 내릴 수 있는 코드
        - 보통 jsp, php 등 간단한 서버 스크립트로 작성된다.
        - 사용자의 입력을 쉘로 전달하는 기능을 수행한다.
    - 서버의 실행 코드를 알아야 하고 (php 서버면 php로, jsp면 jsp로 올려야 함), 업로드한 파일의 경로를 알아야 한다.
* Download 취약점: 웹서버의 홈 디렉토리에서 벗어나 임의의 위치에 있는 파일을 열람하거나 다운로드 할 수 있는 취약점
    - 파일을 열람할 때 경로를 지정할 수 있다면 해당 취약점을 이용하여 소스 코드나 DB 정보 등 주요 정보를 탈취할 수 있다.

### 문제 풀이
* https://dreamhack.io/wargame/challenges/37/
<details>
<summary>Writeup</summary>
<ul>
<li>해당 서버는 /upload 페이지에서는 잘못된 파일 명을 잘 막아두었습니다.</li>
<li>하지만 /read 페이지에서는 파일명을 검토하지 않아, 상대경로 작성이 가능했습니다.</li>
<li>또한, app.py의 7번 줄에서 동일 위치의 flag.py 파일에 FLAG={FLAG} 형태로 플래그가 저장되어있는 것을 확인할 수 있습니다.</li>
<li>따라서 /read 페이지에서 파일명을 ../flag.py로 주면 {root}/upload/../flag.py -> {root}/flag.py 파일 내용, 즉 플래그를 확인할 수 있습니다.</li>
</ul>
</details>
