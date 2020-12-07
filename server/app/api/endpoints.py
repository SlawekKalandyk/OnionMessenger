from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.api.contact_resource import ContactResource
from app.api.message_resource import MessageResource


app = Flask(__name__)
CORS(app)
api = Api()

api.add_resource(ContactResource, '/api/contacts', '/api/contacts/', '/api/contacts/<id>')
api.add_resource(MessageResource, '/api/messages', '/api/messages/', '/api/messages/<id>')

api.init_app(app)