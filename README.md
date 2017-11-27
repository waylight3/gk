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
 * 아직 기초 공사 중입니다. 커밋하지 말아주세요 ㅠㅠ.
