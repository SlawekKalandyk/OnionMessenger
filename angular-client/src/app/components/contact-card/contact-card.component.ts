import { Component, Input, OnInit } from '@angular/core';
import { Contact, ContactState } from 'src/app/model/contact';
import { SocketService } from 'src/app/services/socket-service/socket.service';

@Component({
  selector: 'app-contact-card',
  templateUrl: './contact-card.component.html',
  styleUrls: ['./contact-card.component.css']
})
export class ContactCardComponent implements OnInit {
  @Input() contact!: Contact;

  constructor(private socketService: SocketService) { }

  ngOnInit(): void {
    this.contact.online = ContactState.undetermined;
    this.socketService.getContactOnline().subscribe(contactDto => {
      if(this.contact.contact_id == contactDto.contact_id) {
        this.contact.online = ContactState.online;
      }
    });

    this.socketService.getContactOffline().subscribe(contactDto => {
      if(this.contact.contact_id == contactDto.contact_id) {
        this.contact.online = ContactState.offline;
      }
    });
  }

}
