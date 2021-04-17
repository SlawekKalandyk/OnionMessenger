from app.infrastructure.saved_command import SavedCommand
from app.networking.topology import Agent, Topology
from flask import Flask, g, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from marshmallow import ValidationError

from app.messaging.broker import Broker, Payload
from app.api.commands import ApproveCommand, HelloCommand, MessageCommand
from app.api.socket_emitter import emit_message, emit_new_contact_pending_interlocutor_approval, emit_newly_approved_contact, emit_newly_not_approved_contact
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
    database.create_tables_if_not_exist([Contact, Message, SavedCommand])
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
    
    broker: Broker = InstanceContainer.resolve(Broker)
    command = HelloCommand()
    address = ConnectionSettings(contact.address, TorConfiguration.get_tor_server_port())
    payload = Payload(command, address)
    broker.send(payload)

    emit_new_contact_pending_interlocutor_approval(contact)
    
    return contact_json, 201


@flaskapp.route("/api/contacts/", methods=["GET"])
def get_contacts():
    repository = ContactRepository()
    contacts = repository.get_all()
    as_schema = contacts_schema.dump(list(contacts))
    return jsonify(as_schema), 200


@flaskapp.route("/api/contacts/approved", methods=["GET"])
def get_approved_contacts():
    repository = ContactRepository()
    contacts = repository.get_all_approved()
    as_schema = contacts_schema.dump(list(contacts))
    return jsonify(as_schema), 200


@flaskapp.route("/api/contacts/pending", methods=["GET"])
def get_pending_contacts():
    repository = ContactRepository()
    contacts = repository.get_all_pending()
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

    broker: Broker = InstanceContainer.resolve(Broker)
    command = ApproveCommand(approved=is_approved)
    address = ConnectionSettings(contact.address, TorConfiguration.get_tor_server_port())
    payload = Payload(command, address)
    broker.send(payload)

    if is_approved:
        emit_newly_approved_contact(contact)
    else:
        # if not approved, remove contact, close connection after sending ApproveCommand
        topology: Topology = InstanceContainer.resolve(Topology)
        agent: Agent = topology.get_by_address(contact.address)
        topology.remove(agent)
        agent.close_sockets()
        repository.remove(contact)
        emit_newly_not_approved_contact(contact)

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
    
    broker: Broker = InstanceContainer.resolve(Broker)
    command = MessageCommand(content=message.content, content_type=message.content_type)
    address = ConnectionSettings(message.interlocutor.address, TorConfiguration.get_tor_server_port())
    payload = Payload(command, address)
    broker.send(payload)

    emit_message(message)

    return {}, 204


@flaskapp.route("/api/info/serviceId", methods=["GET"])
def get_hidden_service_address():
    return jsonify(TorConfiguration.get_hidden_service_id()), 200