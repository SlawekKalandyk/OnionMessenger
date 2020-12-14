import { Contact } from './contact';

export enum MessageState {
    SENT = 1,
    RECEIVED = 2
}

export enum MessageAuthor {
    SELF = 1,
    INTERLOCUTOR = 2
}

export enum ContentType {
    STRING = 1,
    IMAGE = 2
}
    
export interface Message {
    contact: Contact
    content: string
    content_type: ContentType
    timestamp: Date
    message_author: MessageAuthor
    message_state: MessageState
}