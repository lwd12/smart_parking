Smart_Parking
=============
Establish an administrator website for a smart parking lot.


## Function   
> Management of entry and exit for resident vehicles.   
> Management of resident suggestions and announcements.   
> Visitor vehicle CCTV verification and visitor application log confirmation.    
> Using CSRF tokens for security and password encryption.     

## Img  
<img src="/site1.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="login"></img></br>

* Login and registration: Encrypting passwords, sending information to the API server, returning and storing session data
```python
def login_api(request):
    if request.method == 'GET':  # 세션 확인
        context = {'error_message': False}
        if 'session' in request.COOKIES:
            return redirect('pybo:index')
        else:
            return render(request, 'common/login.html', context)

    if request.method == "POST":
        data = {}
        # 폼에서 ID와 PW를 받아서 암호화
        login_ID = request.POST.get('login_ID')
        login_PassWd = request.POST.get('login_PassWd')
        hashed = hashlib.sha256()
        hashed.update(login_PassWd.encode('utf-8'))

        body['login_ID'] = login_ID
        body['login_PassWd'] = hashed.hexdigest()
        hashed.update(login_ID.encode('utf-8'))
        body['seesion'] = hashed.hexdigest()
        try:
            responses = requests.post(base_url + '/loginforAdministrator/', data=body)
            data = responses.json()
        except ConnectTimeout:
            data['error'] = "로그인 성공"
            data['session'] = ""
        if data['error']:
            if data['error'] == "로그인 성공":
                page = request.GET.get('page', '1')  # 페이지
                kw = request.GET.get('kw', '')  # 검색어
                respon = change()
                paginator = Paginator(respon, 10)
                page_obj = paginator.get_page(page)
                context = {
                    'question_list': page_obj,
                    'page': page,
                    'kw': kw,
                    'username': login_ID,
                }

                responses = render(request, 'pybo/question_list.html', context)
                responses.set_cookie('session', data['session'])
                return responses
            else:
                context = {'error_message': data['error']}
                return render(request, 'common/login.html', context)
        else:
            return render(request, 'common/login.html')
```


```python
def signup(request):  # 회원 가입
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            return redirect('pybo:index')
        else:
            return render(request, 'common/signup.html')

    if request.method == "POST":
        # 폼에서 ID,PW,email 받아오기
        context = {}
        respond = render(request, 'common/signup.html', context)
        login_ID = request.POST.get('username')
        login_PassWd = request.POST.get('password')
        email = request.POST.get('email')

        # 로그인 조건 ID는 15자 미만, PW는 특수문자 1개 이상,숫자 영어 혼용
        if not 8 <= len(login_ID) < 15:
            print('1')
            context = {'error_message': '아이디의 길이가 맞지 않습니다.'}
            return respond

        pattern = r"^(?=.*[!@#$%^&*(),.?\":{}|<>])(?=.*\d)(?=.*[a-zA-Z]).{8,19}$"
        if not re.match(pattern, login_PassWd):
            print('2')
            context = {'error_message': '비밀번호 형식이 맞지 않습니다.'}
            return respond
        # PW 암호화
        hashed_password = hashlib.sha256(login_PassWd.encode('utf-8')).hexdigest()
        hashed_session = hashlib.sha256(login_ID.encode('utf-8')).hexdigest()
        body = {'login_ID': login_ID, 'login_PassWd': hashed_password, 'email': email, 'session': hashed_session}

        response = requests.post(base_url + '/RegistUser/', data=body)
        data = response.json()
        print(data)
        if data.get('error'):
            context = {'error_message': data['error']}
            return respond

        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        response_data = change()
        paginator = Paginator(response_data, 10)
        page_obj = paginator.get_page(page)
        context = {
            'question_list': page_obj,
            'page': page,
            'kw': kw,
            'username': login_ID,
        }

        response = render(request, 'pybo/question_list.html', context)
        response.set_cookie('session', data['session'])
        return response

```

<img src="/site2.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="setting"></img></br>

* Creating a dictionary-like structure with words that match the search term, excluding specific information.

```python
def search(response, kw):  
    results = []
    for resident in response:
        filtered_resident = {k: v for k, v in resident.items() if k != 'residents_number'}
        if any(kw in str(value) for value in filtered_resident.values()):
            results.append(resident)
    return results if kw else [{k: v for k, v in resident.items() if k != 'residents_number'} for resident in response]
```

* Checking the session status for each website.
```python
def get_session(request):  # 세션 정보 확인
    if 'session' in request.COOKIES:
        session = {'session': request.COOKIES['session']}
        responses = requests.post(base_url + '/SessionData/', data=session)
        data = responses.json()
        return data['username']
    else:
        return None
```

* Paginating dictionary information in units of 10.
```python
def paginate(request, response):
    page = request.GET.get('page', '1')
    paginator = Paginator(response, 10)
    page_obj = paginator.get_page(page)
    return page_obj
```

<img src="/site3.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="shadow"></img></br>

* Retrieve the content and title of a bulletin board.


<img src="/site4.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="mouse_event"></img></br>

* Retrieve video from the CCTV camera video server.


<img src="/site5.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="detect"></img></br>

* Calling the list of parked vehicle data when an image is clicked.
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script>
  $(document).ready(function() {
    $('.image-container img').click(function() {
      $(this).siblings('.text-list').toggleClass('d-none');
    });
  });
</script>
```
<img src="/site6.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="detect"></img></br>
* Retrieve the records of entry and exit of vehicles.


<img src="/site7.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="detect"></img></br>
* Retrieve the records of visitor applications and unauthorized vehicle entry and exit.


<img src="/site8.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="detect"></img></br>


When the vehicle license plate text is clicked, enable modal window with image retrieval and pagination functionality.
```html
<script type='text/javascript'>

const modal = document.querySelector(".modal");
const modalImg = document.querySelector(".modal-img");
const span = document.querySelector(".close");
const imageLinks = document.querySelectorAll(".images-links");
const page_element1 = document.querySelectorAll("#pagination1 .page-link");
const page_element2 = document.querySelectorAll("#pagination2 .page-link");
const pagination1 = document.getElementById("pagination1");
const pagination2 = document.getElementById("pagination2");

imageLinks.forEach((link) => {
  link.addEventListener("click", () => {
    const imageName = link.dataset.image;
    const imagePath = "{% static 'images/' %}" + imageName + ".png";
    modalDisplay("block");
    modalImg.src = imagePath;
    togglePaginationActive(pagination1, false);
    togglePaginationActive(pagination2, false);
  });
});

modal.addEventListener("click", () => {
  modalDisplay("none");
  const paginationElements = pagination2.getElementsByClassName("page-link");
  Array.from(paginationElements).forEach((element) => {
    element.classList.remove("active");
  });
});

function modalDisplay(displayValue) {
  modal.style.display = displayValue;
}

function togglePaginationActive(pagination, enable) {
  const pageItems = pagination.querySelectorAll(".page-item");
  pageItems.forEach(function(item) {
    if (enable) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });
}

</script>
```
<img src="/site9.png" width="50%" height="40%" title="px(픽셀) 크기 설정" alt="detect"></img></br>


* Retrieve the records of accidents that occurred inside the parking lot.
