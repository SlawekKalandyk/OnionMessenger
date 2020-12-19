import { Component, OnInit } from '@angular/core';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { ContentType, MessageAuthor, MessageState } from 'src/app/model/message';
import { ContactService } from 'src/app/services/contact-service/contact.service';
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

  constructor(private messageService: MessageService, private currentContactService: CurrentContactService, private mappingService: DtoMappingService) {
    this.chatMessage = '';
  }

  ngOnInit(): void {
  }

  onSendMessageButtonClick() {
    if (this.chatMessage === '')
      return;

    this.currentContactService.currentContact.subscribe(contact => {
      let message: MessageDto = {
        interlocutor: this.mappingService.mapContactToContactDto(contact),
        content: this.chatMessage,
        content_type: ContentType.STRING,
        timestamp: new Date(),
        message_author: MessageAuthor.SELF,
        message_state: MessageState.SENT
      };
      this.messageService.sendMessage(message).subscribe();
      this.chatMessage = '';
    });
  }
}
