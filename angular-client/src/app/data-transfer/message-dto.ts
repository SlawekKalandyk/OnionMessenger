import { ContentType, MessageAuthor, MessageState } from '../model/message';
import { ContactDto } from './contact-dto';


export interface MessageDto {
    interlocutor: ContactDto
    content: string
    content_type: ContentType
    timestamp: Date
    message_author: MessageAuthor
    message_state: MessageState
}