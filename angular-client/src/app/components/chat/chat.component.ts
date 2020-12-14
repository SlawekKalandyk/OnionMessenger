import { Component, Input, OnInit } from '@angular/core';
import { Contact } from 'src/app/data-transfer/contact';
import { Message } from 'src/app/data-transfer/message';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { CurrentContactService } from 'src/app/services/current-contact-service/current-contact.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  contact!: Contact
  messages: Message[] = []

  constructor(private contactService: ContactService, private currentContactService: CurrentContactService) { }

  ngOnInit(): void {
    this.currentContactService.currentContact.subscribe(currentContact => {
      this.contact = currentContact;
      this.contactService.getMessagesForContact(this.contact.contact_id).subscribe(response => this.messages = response);
    });
  }

}
