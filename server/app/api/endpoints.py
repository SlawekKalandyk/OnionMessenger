from flask import Flask, g, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from marshmallow import ValidationError

from app.messaging.broker import Broker, Payload
from app.messaging.commands import ApproveCommand, MessageCommand
from app.messaging.socket_emitter import emit_contact, emit_message
from app.shared.container import InstanceContainer
from app.shared.config import TorConfiguration
from app.networking.base import ConnectionSettings
from app.infrastructure.database import DatabaseContext
from app.infrastructure.contact import Contact, ContactRepository
from app.infrastructure.message import Message, MessageRepository
from app.api.schemas import ContactSchema, MessageSchema 


flaskapp = Flask(__name__)
CORS(flaskapp)
socketIO = SocketIO(flaskapp, cors_allowed_origins="*")

contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)


def get_and_connect_to_database() -> DatabaseContext:
    database = getattr(g, '_database', None) 
    if not database:
        database = g._database = DatabaseContext().connect_to_database()
    return database


def initdb():
    database = DatabaseContext()
    database.connect_to_database()
    database.create_tables_if_not_exist([Contact, Message])
    database.close()


with flaskapp.app_context():
    initdb()


@flaskapp.before_request
def before_request_start():
    get_and_connect_to_database()


@flaskapp.teardown_request
def on_request_teardown(exception):
    database = getattr(g, '_database', None)
    if database:
        database.close()


@flaskapp.route("/api/contacts/", methods=["POST"])
def add_contact():
    contact_json = request.get_json()
    try:
        contact = contact_schema.load(contact_json)
    except ValidationError:
        return {}, 422

    repository = ContactRepository()
    if repository.get_by_id(contact.contact_id):
        return {}, 409
    
    repository.add(contact)
    emit_contact(contact)
    
    return contact_json, 201


@flaskapp.route("/api/contacts/", methods=["GET"])
def get_contacts():
    repository = ContactRepository()
    contacts = repository.get_all()
    as_schema = contacts_schema.dump(list(contacts))
    return jsonify(as_schema), 200


@flaskapp.route("/api/contacts/<string:id>", methods=["GET"])
def get_contact(id):
    repository = ContactRepository()
    contact = repository.get_by_id(id)
    if not contact:
        return {}, 404
    as_schema = contact_schema.dump(contact)
    return jsonify(as_schema), 200


@flaskapp.route("/api/contacts/<string:id>", methods=["PATCH"])
def change_name(id):
    new_name = request.args.get('name')
    if new_name is None:
        return {}, 400

    repository = ContactRepository()
    contact = repository.get_by_id(id)
    if not contact:
        return {}, 404

    contact.name = new_name
    repository.update(contact)
    as_schema = contact_schema.dump(contact)
    return jsonify(as_schema), 200


@flaskapp.route("/api/contacts/<string:id>", methods=["DELETE"])
def remove_contact(id):
    repository = ContactRepository()
    contact = repository.get_by_id(id)
    if not contact:
        return {}, 404

    repository.remove()
    return {}, 204


@flaskapp.route("/api/contacts/<string:id>/messages", methods=["GET"])
def get_messages_for_contact(id):
    repository = ContactRepository()
    contact = repository.get_by_id(id)
    if not contact:
        return {}, 404

    messages = repository.get_messages(contact)
    as_schema = messages_schema.dump(list(messages))
    return jsonify(as_schema), 200


@flaskapp.route("/api/contacts/<string:id>/approval", methods=["PATCH"])
def approve_contact_for_further_communication(id):
    is_approved = request.args.get('approved')
    if is_approved is None:
        return {}, 400

    repository = ContactRepository()
    contact = repository.get_by_id(id)
    if not contact:
        return {}, 404

    contact.approved = is_approved
    contact.awaiting_approval = False
    repository.update(contact)

    # broker = InstanceContainer.resolve(Broker)
    # command = ApproveCommand(is_approved)
    # address = ConnectionSettings((contact.address, TorConfiguration.get_tor_server_port()))
    # payload = Payload(command, address)
    # broker.send(payload)

    return {}, 204


@flaskapp.route("/api/messages/", methods=["POST"])
def send_message():
    message_json = request.get_json()
    try:
        message = message_schema.load(message_json)
    except ValidationError:
        return {}, 422

    repository = MessageRepository()
    repository.add(message)
    
    broker = InstanceContainer.resolve(Broker)
    command = MessageCommand(source=TorConfiguration.get_hidden_service_id(), content=message.content, content_type=message.content_type)
    address = ConnectionSettings(f'{message.interlocutor.address}.onion', TorConfiguration.get_tor_server_port())
    payload = Payload(command, address)
    broker.send(payload)

    emit_message(message)

    return {}, 204