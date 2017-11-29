# 고래카레
 * [참가자](#참가자)
 * [설치하기](#설치하기)
 * [코드 작성 안내](#코드-작성-안내)
 * [코딩 규칙](#코딩-규칙)

## 참가자
 * 이도현
 * 한중혁
 * 한호재

## 참고자료
 * https://docs.djangoproject.com/ko/1.11
 * http://pythonstudy.xyz/python/article/301-Django-%EC%86%8C%EA%B0%9C

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
 * 내가 만들 구조를 머릿속에 떠올립니다.
 * `url.py`에서 적절한 주소를 할당해줍니다.
   - 인자를 추가로 받으려면 `url(r'^(?P<grouplink>[^/]+)/board/edit/(?P<article_id>\d+)$', views.boardedit, name='boardedit'),`와 같이 작성합니다.
 * `view.py`에서 서버 로직을 처리할 함수를 작성합니다.
   - 함수 이름은 `url.py`에서 설정한 함수 이름과 같아야합니다.
   - 반드시 `request`가 첫 번째 인자여야합니다.
   - 인자를 추가로 받은 경우 `def boardedit(request, grouplink, article_id):`와 같이 작성합니다.
   - 함수의 마지막에는 `return render(request, 'group/edit.html', data)`와 같이 작성하면 됩니다.
 * 해당 페이지의 `.html` 파일을 작성합니다.
   - `{% for c in cctvs %}`
   - `{{ c.name }} / {{ c.pk }}`
   - `{% endfor %}`
   - 위와 같이 `cctvs`를 넘겨주려면 `view.py`에서 `data['cctvs']`에 리스트를 넣어두면 됩니다.
 * 완성!

## 코딩 규칙
 * 들여쓰기는 텝(`tab`)이 아니라 공백 4문자(`spaces: 4`)를 사용합니다.
   - Sublime Text 우측 하단에 `Spaces: 4`라고 뜨는지 확인합니다.
 * `view.py`에서 함수 이름은 소문자로만 구성합니다. 필요한 경우 언더바(`_`)를 사용합니다.
   - 예: `def cctv_info(request, cctv_id):` `def spot_info(request, spot_id):`
 * 해당 변수가 리스트인 경우 변수명이 `s`로 끝나도록 합니다.
   - 예: `cctvs` `spots`
 * `.html` 파일의 이름은 알파벳 소문자와 언더바(`_`)만을 사용합니다.
   - 예: `cctv_info.html`
 * `.html` 파일에서 이터레이터의 이름은 가급적 해당 리스트의 첫 글자로 합니다.
   - `{% for c in cctvs %}` `{% for s in spots %}`
 * `.html` 파일에서 폼 작성시 요소들의 `name`, `id`, `class` 속성에 띄어쓰기가 필요한 경우 중간바(`-`)를 사용합니다.
   - 예: `cctv-name` `spot-name`
 * `view.py`에서 함수와 함수 사이에는 한 칸 띄어씁니다.
   - 예:
```
def aaa(request):
    # code
    # code

def bbb(request):
    # code
    # code
```
 * `view.py`에서 POST 처리가 필요한 경우 다음과 같은 양식을 사용합니다.
```
def aaa(request):
    ret = None
    if request.method == 'POST':
        q = request.POST['query']
        cctv = Cctv.objects.filter(name=q)
        if cctv.count() > 0:
            ret = cctv[0]
        else
            ret = None
    data = {
        'cctvs':ret,
    }
```