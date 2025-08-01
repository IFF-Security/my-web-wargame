## 목차
- [목차](#목차)
- [CDN](#cdn)
- [JS의 Callback](#js의-callback)
- [Node.js](#nodejs)

## CDN
* CDN (Content Delivery Network)
  - 직역하면, 컨텐츠를 전송해주는 네트워크
  - 물리적으로 멀리 떨어져있는 사용자에게 컨텐츠를 더 빨리 제공해주기 위해서 고안된 기술
* CDN을 사용하는 이유
  - 예를 들어, 미국에 있는 클라이언트가 한국에 있는 데이터 서버에 요청을 보낸다고 하자.
  - 만약 CDN을 사용하지 않는다면, 미국에서 한국의 서버까지 요청을 보내야 한다.
    - 이 과정에서 물리적인 통신 지연시간이 발생한다.
  - 이러한 지연시간을 최소화하기 위해, 여러 주요 국가에 서버를 분산시키는 기법이 CDN이다.
* CDN의 캐싱 방식 비교 (Static vs Dynamic)
  |이름|Static|Dynamic|
  |----|----|----|
  |방식|Origin Server의 데이터를 전부 미리 캐싱|요청이 들어온 내용만 캐싱, 만료시점 이후 캐시 삭제|
  |Cache Miss|거의 일어나지 않음|Static 방식보다 잦음|
  |사용 상황|전송할 데이터의 용량이 작거나, 내용이 자주 변하지 않는 경우|전송할 데이터의 용량이 크거나, 내용이 자주 변하는 경우|

## JS의 Callback
* A 함수의 매개변수로 B 함수를 받아, A의 실행 중 B를 실행하는 것
* 예시 코드
  ```js
  function A(callback) {
    console.log("Call A");
    callback();
  }

  function B() {
    console.log("Call B");
  }

  A(B);
  // Result: Call A // Call B
  ```
* 주로 콜백은 해당 함수 호출에서만 사용되기에, 화살표 함수를 사용해 임시 함수를 콜백 함수로 전달한다.
* 예시 코드
  ```js
  function A(callback) {
    console.log("Call A");
    callback();
  }

  A(() => console.log("Arrow Function!"));
  // Result: Call A // Arrow Function!
  ```

## Node.js
* JS는 기본적으로 브라우저의 JS 해석 엔진에 의해 실행됨
  - 때문에 기존의 JS 코드는 브라우저에서만 실행이 가능했음
* 그러던 중, 구글의 Chrome 출시 당시 사용한 V8 엔진이 공개됨
  - V8 엔진은 매우 빠르고, 소스도 공개되어있었음
  - 이러한 특징을 발판 삼아 V8 엔진을 기반으로 한 Node 프로젝트가 진행됨
  - 그 결과 나온 것이 바로 Node.js라는 JS Runtime
* Non-Blocking Response 덕분에 개수는 많지만 크기는 작은 데이터를 빠르게 주고받는 데에 용이하여, SNS나 실시간 차트 등에 적합함
* 그러나 싱글스레드라는 한계를 벗어나지 못하기에 CPU를 많이 점유하는 이미지, 비디오, 대규모 데이터 처리에는 적합하지 않음
