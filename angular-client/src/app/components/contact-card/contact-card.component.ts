import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { QuestionRemoveContactDialogComponent } from 'src/app/dialogs/question-remove-contact-dialog/question-remove-contact-dialog.component';
import { Contact, ContactState } from 'src/app/model/contact';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { SocketService } from 'src/app/services/socket-service/socket.service';

@Component({
  selector: 'app-contact-card',
  templateUrl: './contact-card.component.html',
  styleUrls: ['./contact-card.component.css']
})
export class ContactCardComponent implements OnInit {
  @Input() contact!: Contact;
  displayButtons: boolean = false;

  constructor(public dialog: MatDialog, private socketService: SocketService, private contactService: ContactService) { }

  ngOnInit(): void {
    this.socketService.getContactOnline().subscribe(contactDto => {
      if (this.contact.contact_id == contactDto.contact_id) {
        this.contact.online = ContactState.online;
      }
    });

    this.socketService.getContactOffline().subscribe(contactDto => {
      if (this.contact.contact_id == contactDto.contact_id) {
        this.contact.online = ContactState.offline;
      }
    });
  }

  onMouseEnter() {
    this.displayButtons = true;
  }

  onMouseLeave() {
    this.displayButtons = false;
  }
  
  onDelete() {
    const dialogRef = this.dialog.open(QuestionRemoveContactDialogComponent, {
      width: '600px',
      data: { contactId: this.contact.contact_id }
    });
  }
}
