from flask import request
from flask_restful import Resource

# API를 만들기 위한 클래스를 작성(class란? 변수와 함수로 구성된 묶음)
# 클래스는 상속이 가능하다
# API를 만들기 위해서는 flask_restful 라이브러리의 Resource 클래스를 상속해서 만들어야 한다
class RecipeListResource(Resource) :
    # API를 처리하는 함수 개발
    # HTTP Method를 보고 똑같이 만들어준다
    def post(self) : 
        # 1. 클라이언트가 보내준 데이터가 있으면 그 데이터를 받아준다
        data = request.get_json()
        # print(data) 디버깅용

        # 2. 이 레시피 정보를 DB에 저장해야한다
        

        # API를 끝낼때는 클라이언트에 보내줄 정보(json)와 http 상태코드를 리턴한다(보내준다)
        return {"result" : "success"}, 200