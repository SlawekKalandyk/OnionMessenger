import { Contact } from './contact';

enum MessageState {
    SENT = 1,
    RECEIVED = 2
}

enum MessageAuthor {
    SELF = 1,
    INTERLOCUTOR = 2
}

enum ContentType {
    STRING = 1,
    IMAGE = 2
}
    
export interface Message {
    contact: Contact
    content: Uint8Array
    content_type: ContentType
    timestamp: Date
    message_author: MessageAuthor
    message_state: MessageState
}