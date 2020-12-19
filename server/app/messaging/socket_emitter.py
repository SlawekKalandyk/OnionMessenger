from app.api.schemas import ContactSchema, MessageSchema
from flask_socketio import SocketIO

from app.shared.container import InstanceContainer


def emit_message(message):
    message_schema = MessageSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('message', message_schema.dump(message))


def emit_contact(contact):
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('contact', contact_schema.dump(contact))