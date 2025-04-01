# 프레임워크 로드 
from flask import Flask, request, render_template, url_for, redirect, session
import pandas as pd
import invest
from database import MyDB
from dotenv import load_dotenv
import os
from data import querys

# .env 파일 로드 
load_dotenv()

# Flask Class 생성 
app = Flask(__name__)

# session에 비밀키 지정 
app.secret_key = os.getenv('secret')

# database Class 생성 
mydb = MyDB(
    host = os.getenv('host'), 
    port = int(os.getenv('port')), 
    user = os.getenv('user'), 
    pwd = os.getenv('pwd'), 
    db = os.getenv('db')
)

# 테이블 생성하는 쿼리를 실행 
mydb.execute_query(querys.create_query)

# / api 생성
@app.route('/')
def index():
    return render_template('index.html')

# 회원 가입 페이지로 이동하는 api 생성 
@app.route('/signup')
def signup():
    return render_template('signup.html')

# 로그인 api
@app.route('/signin', methods=['post'])
def signin():
    input_id = request.form['id']
    input_pass = request.form['password']

    login_result = mydb.execute_query(
        querys.login_query, 
        input_id, 
        input_pass
    )
    # login_result의 길이가 1이면 로그인 성공 
    if len(login_result) == 1:
        # 로그인 성공시 세션에 데이터 저장
        session['user_info'] = [input_id, input_pass]
        return redirect('/invest')
    else:
        return redirect('/')

# 회원 가입 api 
@app.route('/signup2', methods=['post'])
def signup2():
    # id, password, name 데이터를 받아온다. 
    input_id = request.form['id']
    input_pass = request.form['password']
    input_name = request.form['name']

    # 사용가능한 아이디인가 확인 
    check_result = mydb.execute_query(querys.check_query, input_id)
    # check_result는 df
    if len(check_result) == 0:
        # 사용 가능한 아이디 
        mydb.execute_query(querys.signup_query, 
                            input_id, 
                            input_pass, 
                            input_name, 
                            inplace = True)
        return redirect("/")
    else:
        return redirect('signup')

# 유저가 어떤 종목, 투자기간, 투자 전략 방식을 입력할수 있는 
# 페이지를 보여주는 api 생성
@app.route('/invest')
def first():
    # session에 데이터가 존재하는가?
    if 'user_info' in session:
        return render_template('invest.html')
    else:
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_info' not in session:
        return redirect('/')
    # 유저가 보낸 데이터를 변수에 저장 
    # get 방식으로 보내온 데이터는 request.args에 존재 
    # 종목코드 
    input_code = request.args['code']
    # 시작 시간
    input_year = request.args['year']
    input_month = request.args['month']
    input_day = request.args['day']
    input_time = f"{input_year}-{input_month}-{input_day}"
    # 투자 방식
    input_type = request.args['type']
    # 데이터를 로드 
    df = invest.load_data(input_code, input_time)
    # Class 생성 
    invest_class = invest.Invest(df, 
                                _col='Close', 
                                _start=input_time)
    # input_type을 기준으로 Class의 함수를 호출
    if input_type == 'bnh':
        result = invest_class.buyandhold()
    elif input_type == 'boll':
        result = invest_class.bollinger()
    elif input_type == 'mmt':
        result = invest_class.momentum()
    # 특정 컬럼만 필터
    result = result[['Close','trade', 'rtn', 'acc_rtn']]
    # 특정 컬럼을 생성
    result['ym'] = result.index.strftime('%Y-%m')
    # 테이블을 정제 
    result = pd.concat(
        [
            result.groupby('ym')[['Close', 'trade', 'acc_rtn']].max(),
            result.groupby('ym')[['rtn']].mean()
        ], axis=1
    )
    result.reset_index(inplace=True)
    # 컬럼의 이름을 변경 
    result.columns = ['시간', '종가', '보유내역', 
                        '누적 수익율', '일별 수익율']
    # 컬럼들의 이름을 리스트로 생성
    cols_list = list(result.columns)
    # 테이블에 데이터
    dict_data = result.to_dict(orient='records')
    # x축 데이터 
    x_data =  list(result['시간'])
    # y축 데이터 
    y_data = list(result['일별 수익율'])
    y1_data = list(result['누적 수익율'])
    return render_template('dashboard.html', 
                            table_cols = cols_list, 
                            table_data = dict_data, 
                            x_data = x_data, 
                            y_data = y_data, 
                            y1_data = y1_data)
