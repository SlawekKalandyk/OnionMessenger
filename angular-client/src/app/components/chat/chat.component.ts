import { Component, Input, OnInit } from '@angular/core';
import { Contact } from 'src/app/model/contact';
import { Message } from 'src/app/model/message';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { CurrentContactService } from 'src/app/services/current-contact-service/current-contact.service';
import { DtoMappingService } from 'src/app/services/dto-mapping-service/dto-mapping.service';
import { MessageService } from 'src/app/services/message-service/message.service';
import { SocketService } from 'src/app/services/socket-service/socket.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  contact!: Contact
  messages: Message[] = []

  constructor(private contactService: ContactService, private currentContactService: CurrentContactService, 
    private socketService: SocketService, private mappingService: DtoMappingService) { }

  ngOnInit(): void {
    this.currentContactService.currentContact.subscribe(currentContact => {
      this.contact = currentContact;
      this.contactService.getMessagesForContact(this.contact.contact_id)
        .subscribe(response => this.messages = response.map(messageDto => this.mappingService.mapMessageDtoToMessage(messageDto)));
    });

    this.socketService.getMessages().subscribe(messageDto => {
      if(messageDto.interlocutor.contact_id == this.contact.contact_id) {
        let message = this.mappingService.mapMessageDtoToMessage(messageDto);
        this.messages.unshift(message);
      }
    })
  }
}
