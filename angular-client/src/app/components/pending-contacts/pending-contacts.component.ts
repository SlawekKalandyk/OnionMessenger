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
    this.socketService.getContacts().subscribe(contactDto => {
      if (contactDto.awaiting_approval == true) {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        if(contact.approved) {
          this.waitingForInterlocutorApprovalContacts.push(contact);
        } else {
          this.waitingForUserApprovalContacts.push(contact);
        }
      }
    })
  }

}
