# 고래카레
 * [참가자](#참가자)
 * [설치하기](#설치하기)
 * [코드 작성 안내](#코드-작성-안내)

## 참가자
 * 이도현
 * 한중혁
 * 한호재

## 설치하기
 * python 3.5 이상 (virtualenv 가상환경 사용 권장)
 * Django 1.11 이상
   - `pip install django`
 * pymysql
   - `pip install pymysql`
 * mysql 설치 후 다음 각 부분에서의 utf-8 설정 확인할 것
   - mysql 전체 설정
   - 새로 생성되는 전체 테이블 설정
   - 미리 테이블을 만들어둔 경우 위의 설정이 적용되지 않으므로 직접 수정해야 함
     + 현존하는 모든 테이블 각각의 설정
     + 각 테이블의 모든 열 각각의 설정
 * mysql에서 gk 데이터베이스 생성해둘 것
   - `create database gk;`
   - `show databases;`로 확인 가능
 * mysql root 계정 비밀번호 `password.stt`에 저장할 것 (`manage.py`와 같은 레벨에 둘 것)
   - `.stt`는 `.gitignore`에 등록되어있으므로 직접 생성하여 사용해야 함

## 코드 작성 안내
 1. 내가 만들 구조를 머릿속에 떠올립니다.
 1. `url.py`에서 적절한 주소를 할당해줍니다.
   1. 인자를 추가로 받으려면 `url(r'^(?P<grouplink>[^/]+)/board/edit/(?P<article_id>\d+)$', views.boardedit, name='boardedit'),`와 같이 작성합니다.
 1. `view.py`에서 서버 로직을 처리할 함수를 작성합니다.
   1. 함수 이름은 `url.py`에서 설정한 함수 이름과 같아야합니다.
   1. 반드시 `request`가 첫 번째 인자여야합니다.
   1. 인자를 추가로 받은 경우 `def boardedit(request, grouplink, article_id):`와 같이 작성합니다.
 1. 해당 페이지의 `.html` 파일을 작성하고 `view.py`와 연결해줍니다.
   1. `return render(request, 'group/edit.html', data)`와 같이 작성하면 됩니다.
   1. 추가로 프론트 작업을 진행합니다.
 1. 완성!