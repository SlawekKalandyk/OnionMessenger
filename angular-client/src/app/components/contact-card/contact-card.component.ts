import { Component, Input, OnInit } from '@angular/core';
import { Contact, ContactState } from 'src/app/data-transfer/contact';
import { CurrentContactService } from 'src/app/services/current-contact-service/current-contact.service';

@Component({
  selector: 'app-contact-card',
  templateUrl: './contact-card.component.html',
  styleUrls: ['./contact-card.component.css']
})
export class ContactCardComponent implements OnInit {
  @Input() contact!: Contact;

  constructor() { }

  ngOnInit(): void {
    this.contact.online = ContactState.online;
  }

}
