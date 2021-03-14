import { Component, OnInit } from '@angular/core';
import { Contact } from 'src/app/model/contact';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { DtoMappingService } from 'src/app/services/dto-mapping-service/dto-mapping.service';
import { SocketService } from 'src/app/services/socket-service/socket.service';

@Component({
  selector: 'app-pending-contacts',
  templateUrl: './pending-contacts.component.html',
  styleUrls: ['./pending-contacts.component.css']
})
export class PendingContactsComponent implements OnInit {
  waitingForUserApprovalContacts: Contact[] = []
  waitingForInterlocutorApprovalContacts: Contact[] = []

  constructor(private contactService: ContactService, private mappingService: DtoMappingService, private socketService: SocketService) { }

  ngOnInit(): void {
    this.contactService.getAllPendingContacts().subscribe(response => {
      let allContacts = response.map(contactDto => this.mappingService.mapContactDtoToContact(contactDto));
      this.waitingForUserApprovalContacts = allContacts.filter(contact => !contact.approved)
      this.waitingForInterlocutorApprovalContacts = allContacts.filter(contact => contact.approved);
    });

    this.socketService.getNewContactPendingInterlocutorApproval().subscribe(contact => {
      this.waitingForInterlocutorApprovalContacts.push(contact);
    });

    this.socketService.getNewContactPendingSelfApproval().subscribe(contact => {
      this.waitingForUserApprovalContacts.push(contact);
    });

    this.socketService.getNewlyNotApprovedContact().subscribe(contact => {
      this.removeContactFromPending(contact);
    });

    this.socketService.getNewlyApprovedContact().subscribe(contact => {
      this.removeContactFromPending(contact);
    });

    this.socketService.getReceivedContactApproval().subscribe(contact => {
      this.removeContactFromPending(contact);
    });
  }

  private removeContactFromPending(contact: Contact) {
    let pendingForUserApprovalIndex = this.waitingForUserApprovalContacts.findIndex(c => c.contact_id == contact.contact_id);
    if (pendingForUserApprovalIndex > -1) {
      this.waitingForUserApprovalContacts.splice(pendingForUserApprovalIndex, 1);
      return;
    }

    let pendingForInterlocutorApprovalIndex = this.waitingForInterlocutorApprovalContacts.findIndex(c => c.contact_id == contact.contact_id);
    if (pendingForInterlocutorApprovalIndex > -1) {
      this.waitingForInterlocutorApprovalContacts.splice(pendingForInterlocutorApprovalIndex, 1);
      return;
    }
  }
}
