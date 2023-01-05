from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from myspl_connection import get_connection
from mysql.connector import Error
from email_validator import validate_email, EmailNotValidError
from utils import check_password, hash_password

class UserRegisterResource(Resource) :
    
    def post(self) :
        #{"username": "홍길동",
        #"email": "abc@naver.com",
        #"password": "1234"}

        # 1. 클라이언트가 보낸 데이터를 받아준다
        data = request.get_json()

        # 2. 이메일주소 형식이 올바른지 확인한다
        try :
            validate_email( data["email"] )
        except EmailNotValidError as e :
            print(str(e))
            return {'error' : str(e)}, 400

        # 3. 비밀번호의 길이가 유효한지 체크한다
        # 비번이 4자리 이상 12자리 이하면 에러 (정상이 아닐때 코드를 먼저 작성)
        if len(data["password"]) < 4 or len(data["password"]) > 12 :
            return {'error' : '비밀번호 길이 확인'}, 400

        # 4. 비밀번호를 암호화한다
        hashed_password = hash_password(data["password"])
        print(hashed_password)

        # 5. DB에 회원정보를 저장한다
        try :
            connection = get_connection()

            query = '''insert into user
                    (username, email, password)
                    values
                    (%s, %s, %s);'''
            
            record = (data["username"], data["email"], hashed_password)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            # DB에 회원가입하여 insert 된 후에 user테이블의 id값을 가져오는 코드
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500

        # 보안상 유저 아이디를 바로 클라이언트에게 보내면 안되고 JWT로 암호화해서 인증토큰을 보낸다
        # create_access_token(user_id, expires_delta= datetime.timedelta(minutes=30)) expires_delta= 만료시간주는 것(일, 시, 분)

        access_token = create_access_token(user_id) # 여러개는 딕셔너리로 입력
        return {"result" : "success", "access_token" : access_token}, 200

class UserLoginResource(Resource) :

    def post(self) :
        # {"email": "abc@naver.com",
        # "password": "1234"}

        # 1. 데이터 받아오기
        data = request.get_json()

        # 2. DB로부터 해당 유저의 데이터를 가져온다
        try :
            connection = get_connection()

            query = '''select *
                    from user
                    where email = %s ;'''

            record = (data["email"], )

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            # 가져온 결과가 없을때 처리 (=회원가입 하지 않은 사람)
            if len(result_list) == 0 :
                return {"error" : "회원가입한 사람이 아닙니다"} , 400

            # 시간을 문자열로 변환
            i = 0
            for row in result_list :
                result_list[i]['created_at'] = row['created_at'].isoformat()
                result_list[i]['updated_at'] = row['updated_at'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500

        print(result_list)

        # 3. 비밀번호가 맞는지 확인한다
        check = check_password( data['password'], result_list[0]['password'] )

        if check == False :
            return {"error" : "비밀번호가 일치하지 않습니다"} , 400

        # 4. JWT 토큰을 만들어서 클라이언트에게 보낸다
        access_token = create_access_token( result_list[0]['id'] )

        return {"result" : "success", "access_token" : access_token}, 200

# 로그아웃된 토큰을 저장할 셋(set)을 만든다
jwt_blacklist = set()

class UserLogoutResource(Resource) :

    @jwt_required()
    def post(self) :
        
        jti = get_jwt()['jti']
        print(jti)

        jwt_blacklist.add(jti)

        return {'result' : 'success'}, 200