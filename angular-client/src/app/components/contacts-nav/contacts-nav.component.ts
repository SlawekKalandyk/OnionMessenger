import { Component, OnInit } from '@angular/core';
import { of } from 'rxjs';
import { Contact } from 'src/app/data-transfer/contact';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { CurrentContactService } from 'src/app/services/current-contact-service/current-contact.service';

@Component({
  selector: 'app-contacts-nav',
  templateUrl: './contacts-nav.component.html',
  styleUrls: ['./contacts-nav.component.css']
})
export class ContactsNavComponent implements OnInit {
  contacts: Contact[] = []
  currentContact!: Contact
  
  constructor(private contactService: ContactService, private currentContactService: CurrentContactService) { }

  ngOnInit(): void {
    this.contactService.getAllContacts().subscribe(response => this.contacts = response);
    if(this.contacts.length > 0) {
      this.currentContactService.currentContact = of(this.contacts[0]);
    }

    this.currentContactService.currentContact.subscribe(response => this.currentContact = response)
  }

  onSelect(contact: Contact) {
    this.currentContactService.currentContact = of(contact);
  }
}
