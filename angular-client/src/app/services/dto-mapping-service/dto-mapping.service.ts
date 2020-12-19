import { Injectable } from '@angular/core';
import { ContactDto } from 'src/app/data-transfer/contact-dto';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { Contact, ContactState } from 'src/app/model/contact';
import { Message } from 'src/app/model/message';

@Injectable({
  providedIn: 'root'
})
export class DtoMappingService {

  constructor() { }

  mapContactToContactDto(contact: Contact) {
    let contactDto: ContactDto = {
      contact_id: contact.contact_id,
      name: contact.name,
      address: contact.address,
      approved: contact.approved,
      awaiting_approval: contact.awaiting_approval
    };
    return contactDto;
  }

  mapContactDtoToContact(contactDto: ContactDto) {
    let contact: Contact = {
      ...contactDto,
      online: ContactState.undetermined
    }
    return contact;
  }

  mapMessageToMessageDto(message: Message) {
    let messageDto: MessageDto = {
      interlocutor: this.mapContactToContactDto(message.interlocutor),
      content: message.content,
      content_type: message.content_type,
      timestamp: message.timestamp,
      message_author: message.message_author,
      message_state: message.message_state
    }
    return messageDto;
  }

  mapMessageDtoToMessage(messageDto: MessageDto) {
    let message: Message = {
      interlocutor: this.mapContactDtoToContact(messageDto.interlocutor),
      content: messageDto.content,
      content_type: messageDto.content_type,
      timestamp: messageDto.timestamp,
      message_author: messageDto.message_author,
      message_state: messageDto.message_state
    }
    return message;
  }
}
