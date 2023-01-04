from flask import Flask
from flask_restful import Api
from config import Config
from resources.recipe import RecipeListResource, RecipePublishResource, RecipeResource

app = Flask(__name__)
# 환경변수 셋팅
app.config.from_object(Config)

api = Api(app)

# 경로와 리소스(API코드)를 연결한다
api.add_resource(RecipeListResource, '/recipes')
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')

if __name__ == '__main__' :
    app.run()