## 목차
- [목차](#목차)
- [dockerfile 확인](#dockerfile-확인)
- [Route별 코드 확인](#route별-코드-확인)
  - [/ (index)](#-index)
  - [/mkfile](#mkfile)
  - [/readfile](#readfile)
  - [/test](#test)
- [Prototype Pollution](#prototype-pollution)
  - [JS의 `__proto__` 필드](#js의-__proto__-필드)
  - [`setValue` 함수가 취약한 이유](#setvalue-함수가-취약한-이유)
- [문제의 해결 과정](#문제의-해결-과정)

## dockerfile 확인
* 4번 줄 -> 컨테이너의 root에 flag 파일을 생성함
  - flag 파일(target)의 위치 확인
* 6, 8번 줄 -> dockerfile을 포함한 로컬 파일들은 /app 폴더로 복사됨

## Route별 코드 확인
### / (index)
* 쿼리 매개변수: X
* 동작
  - `read['filename']`을 "fake"로 설정
  - ejs 폴더의 index.ejs 파일을 렌더링해서 보여줌

### /mkfile
* 쿼리 매개변수: filename, content
* 동작
  - filename를 sha256으로 hash하여 파일명으로 사용
  - 해당 이름으로 저장에 성공했다면, `file` 전역변수에 해싱된 filename를 저장함

### /readfile
* 쿼리 매개변수: filename
* 동작
  - 주어진 `filename`이 `file` 전역변수에 저장되어있는지 확인
  - 저장되어있지 않다면, `read` 전역변수의 "filename" 필드에 해당하는 파일을 읽어옴
  - 저장되어있다면, 다음의 동작을 수행함
    - `read` 전역변수에 filename에서 `.`을 모두 삭제해 저장
    - 해당 필터링된 filename에 해당하는 파일을 읽어옴
    - **이로 인해 filename에 `..`를 이용해 Path Traversal 공격을 하는 것은 불가능함**
  - 주어진 filename에 대해, `./storage/{filename}` (즉, `/app/storage/{filename}`)를 읽어옴
    - flag 파일은 `/`에 있으므로, flag 파일을 읽어오기 위해서는 `read` 매개변수에 `../../flag`가 저장되어야 함

### /test
* 쿼리 매개변수: func, filename(선택), rename(선택)
* 동작
  - func이 reset이라면, `read` 전역변수를 `{}`로 초기화함
  - func이 rename이라면, `setValue` 함수를 이용해 `file` 전역변수의 filename 필드를 rename으로 변경함
* 취약점
  - `setValue` 함수는 key를 `.`를 기준으로 잘라, 재귀적으로 오브젝트를 업데이트한다.
    - 이 과정에서 현재 추가중인 key에 대한 검사를 진행하지 않고 업데이트를 진행한다.
    - 이 특성으로 인해, Prototype Pollution 취약점이 발생한다!

## Prototype Pollution
### JS의 `__proto__` 필드
* JS는 prototype으로 상속을 구현한다.
  - 예를 들어, class B가 class A의 상속을 받는다면, B의 prototype 중 `__proto__` 필드가 A의 prototype을 가리키는 형식이다.
  - 이 `__proto__` 필드는 클래스별로 동일하게 유지된다.
* Object 또한 다른 클래스와 동일하게 prototype에 `__proto__` 필드를 가지며, Object의 `__proto__`의 `__proto__`는 `null`을 가리킨다.
* 이 프로젝트에서 `file`과 `read` 전역변수는 모두 Object의 인스턴스인 `{}`로 선언되었으며, 따라서 동일한 `__proto__`를 가진다.
* 또한, 상속받은 클래스의 필드에 접근할 때, 해당 필드가 클래스 자체에 없다면 `__proto__` 필드를 타고 올라가며 해당 필드가 있는지 확인한다.

### `setValue` 함수가 취약한 이유
* `__proto__` 필드는 다른 필드와 동일하게 `obj["__proto__"]`와 같은 방식으로 접근할 수 있다.
* 때문에, `setValue` 함수의 `obj`에 Object를, `key`를 `__proto__.`으로 시작하도록 설정한다면 Object의 prototype를 수정할 수 있다.
* 이러한 취약점을 prototype의 오염, 즉 `Prototype Pollution` 이라 한다.

## 문제의 해결 과정
1. `/test` Route를 통해 Object의 Property를 수정한다.
 - func=`rename`, filename=`__proto__.filename`, rename=`../../flag`로 지정한다.
   - full payload: `{domain}/test?func=remote&filename=__proto__.filename&rename=../../flag`
 - 필드 이름을 "filename"으로 설정한 이유는 `/readfile` Route의 처리 방식 때문이다.
   - `/readfile` Route는 `file` 전역변수에 지정한 파일명이 있다면 파일을 읽기 전에 `read` 전역변수에서 filename에 해당하는 값을 덮어써버린다.
   - 때문에 `file`에 없는 파일명을 사용해야 하며, 그에 따라 `read['filename']`에 해당하는 파일만 확인할 수 있다.
   - 그러나 `read`의 필드를 필터 없이 인워적으로 수정할 수 있는 곳은 없다.
   - 따라서 `file`의 `__proto__`에 filename 필드를 추가해 `read`에서도 filename 필드에 접근할 수 있도록 해야한다.
  - 결과적으로, `setValue(file, "__proto__.filename", "../../flag")`가 실행되어 모든 Object에 대해 `obj["filename"] == "../../flag"`가 된다.
2. `/readfile` Route를 통해 Flag를 획득한다.
 - 이 때, 쿼리 매개변수로 저장한 `filename`은 `file` 전역변수에 존재하지 않아야 한다.
 - 적당히 filename=`asdfasdfasdfasdf` 정도로 지정하고 요청하면 된다.
 - 결과적으로, `/flag` 파일을 읽어와 flag를 획득할 수 있다. 
