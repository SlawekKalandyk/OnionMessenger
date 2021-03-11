import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { of } from 'rxjs';
import { ContactDto } from 'src/app/data-transfer/contact-dto';
import { AddContactDialogData } from 'src/app/dialogs/add-contact-dialog/add-contact-dialog-data';
import { AddContactDialogComponent } from 'src/app/dialogs/add-contact-dialog/add-contact-dialog.component';
import { Contact, ContactState } from 'src/app/model/contact';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { CurrentContactService } from 'src/app/services/current-contact-service/current-contact.service';
import { DtoMappingService } from 'src/app/services/dto-mapping-service/dto-mapping.service';
import { SocketService } from 'src/app/services/socket-service/socket.service';

@Component({
  selector: 'app-contacts-nav',
  templateUrl: './contacts-nav.component.html',
  styleUrls: ['./contacts-nav.component.css']
})
export class ContactsNavComponent implements OnInit {
  contacts: Contact[] = []
  currentContact!: Contact

  constructor(public dialog: MatDialog, private contactService: ContactService, private currentContactService: CurrentContactService,
    private socketService: SocketService, private mappingService: DtoMappingService) { }

  ngOnInit(): void {
    this.contactService.getAllApprovedContacts().subscribe(response => this.contacts = response.map(contactDto => this.mappingService.mapContactDtoToContact(contactDto)));
    if (this.contacts.length > 0) {
      this.currentContactService.currentContact = of(this.contacts[0]);
    }

    this.currentContactService.currentContact.subscribe(response => this.currentContact = response)
    this.socketService.getContacts().subscribe(contactDto => {
      if (contactDto.approved && !contactDto.awaiting_approval) {
        let newContact = this.mappingService.mapContactDtoToContact(contactDto);
        let existingContactIndex = this.contacts.findIndex(contact => contact.contact_id === contactDto.contact_id);
        
        if (existingContactIndex > -1) {
          this.contacts[existingContactIndex] = newContact;
        } else {
          newContact.online = ContactState.online;
          this.contacts.push(newContact);
        }
      }
    });
  }

  onSelect(contact: Contact) {
    this.currentContactService.currentContact = of(contact);
  }

  openAddContactDialog() {
    const dialogRef = this.dialog.open(AddContactDialogComponent, {
      width: '600px',
      data: { name: '', address: '' }
    });

    dialogRef.afterClosed().subscribe(result => {
      let contact: ContactDto = {
        contact_id: result.address,
        name: result.name,
        approved: true,
        awaiting_approval: true,
        address: result.address + '.onion',
      };
      this.contactService.addContact(contact).subscribe();
    });
  }
}
