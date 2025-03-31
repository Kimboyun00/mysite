# 프레임워크 로드
from flask import Flask, request, render_template, url_for
import pandas as pd
import invest


# Flask Class 생성
app = Flask(__name__)

# 유저가 어떤 종목, 투자 기간, 투자 전략 방식을 입력할 수 있는
# 페이지를 보여주는 api 생성
@app.route('/invest')
def invest():
    return render_template('invest.html')


# 대쉬보드 페이지를 보여주는 api 생성
# 대쉬보드에서 필요한 데이터는
# table_cols (표에서 컬럼의 이름들) list
# table_data (표에서 밸류의 값들) dict
# x_data (차트에서 x축 데이터) list
# y_data (차트에서 y축 데이터) list
@app.route('/dashboard')
def dashboard():
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
                                _col = 'Close',
                                _start = input_time)
    # input_type을 기준으로 Class의 함수를 호출
    if input_type == 'bnh':
        result = invest_class.buyandhold()
    elif input_type == 'boll':
        result = invest_class.bollinger()
    elif input_type == 'mmt':
        result = invest_class.momentum()
    # 인덱스를 초기화
    result.reset_index(inplace = True)
    # 특정 컬럼만 필터
    result = result[['Date', 'Close', 'trade', 'rtn', 'acc_trn']]
    # 컬럼의 이름을 변경
    result.columns = ['시간', '종가', '보유내역','일별 수익률', '누적 수익률']
    # 컬럼들의 이름을 리스트로 생성
    cols_list = list(result.columns)
    # 테이블에 데이터
    dict_data = result.to_dict(orient='records')
    # x축 데이터
    x_data = list(result['시간'])
    # y축 데이터
    y_data = list(result['일별 수익률'])
    y1_data = list(result['월별 수익률'])
    return render_template('/dashboard.html',
                            table_cols = cols_list,
                            table_data = dict_data,
                            x_data = x_data,
                            y_data = y_data,
                            y1_data = y1_data)



app.run(debug=True)