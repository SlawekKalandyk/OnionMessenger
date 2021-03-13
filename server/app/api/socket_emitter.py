from app.api.schemas import ContactSchema, MessageSchema
from flask_socketio import SocketIO

from app.shared.container import InstanceContainer


def emit_message(message):  
    message_schema = MessageSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('message', message_schema.dump(message))


def emit_new_contact_pending_interlocutor_approval(contact):
    """
    Called after sending a Hello command. Contact is pending for interlocutor approval.
    """
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('new-contact-pending-interlocutor-approval', contact_schema.dump(contact))


def emit_new_contact_pending_self_approval(contact):
    """
    Called after receiving a Hello command. Contact is pending for user approval.
    """
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('new-contact-pending-self-approval', contact_schema.dump(contact))


def emit_newly_approved_contact(contact):
    """
    Called after sending an Approve command with further communication approval. Contact state (on/off) is off.
    """
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('approved-contact', contact_schema.dump(contact))


def emit_newly_not_approved_contact(contact):
    """
    Called after sending an Approve command without further communication approval.
    """
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('not-approved-contact', contact_schema.dump(contact))


def emit_received_contact_approval(contact):
    """
    Called after receiving an Approve command. Contact state (on/off) is on.
    """
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('received-approved-contact', contact_schema.dump(contact))


def emit_contact_offline(contact):
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('contact-offline', contact_schema.dump(contact))


def emit_contact_online(contact):
    contact_schema = ContactSchema()
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('contact-online', contact_schema.dump(contact))


def emit_service_start():
    socket: SocketIO = InstanceContainer.resolve(SocketIO)
    socket.emit('hidden-service-start', None)