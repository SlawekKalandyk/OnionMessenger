import { Component, OnInit } from '@angular/core';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { Contact } from 'src/app/model/contact';
import { ContentType, MessageAuthor, MessageState } from 'src/app/model/message';
import { CurrentContactService } from 'src/app/services/current-contact-service/current-contact.service';
import { DtoMappingService } from 'src/app/services/dto-mapping-service/dto-mapping.service';
import { MessageService } from 'src/app/services/message-service/message.service';

@Component({
  selector: 'app-chat-box',
  templateUrl: './chat-box.component.html',
  styleUrls: ['./chat-box.component.css']
})
export class ChatBoxComponent implements OnInit {
  chatMessage: string
  currentContact: Contact | undefined;

  constructor(private messageService: MessageService, private currentContactService: CurrentContactService, private mappingService: DtoMappingService) {
    this.chatMessage = '';
  }

  ngOnInit(): void {
    this.currentContactService.currentContact.subscribe(contact => {
      this.currentContact = contact;
      this.chatMessage = '';
    });
  }

  onSendMessageButtonClick() {
    if (this.chatMessage === '' || this.currentContact === undefined)
      return;

    let message: MessageDto = {
      interlocutor: this.mappingService.mapContactToContactDto(this.currentContact),
      content: this.chatMessage,
      content_type: ContentType.STRING,
      timestamp: new Date(),
      message_author: MessageAuthor.SELF,
      message_state: MessageState.SENT
    };

    this.messageService.sendMessage(message).subscribe();
    this.chatMessage = '';

  }
}
