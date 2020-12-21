import { Component, Input, OnInit } from '@angular/core';
import { Contact } from 'src/app/model/contact';
import { ContactService } from 'src/app/services/contact-service/contact.service';

@Component({
  selector: 'app-pending-contact-card',
  templateUrl: './pending-contact-card.component.html',
  styleUrls: ['./pending-contact-card.component.css']
})
export class PendingContactCardComponent implements OnInit {
  @Input() contact!: Contact;
  displayButtons: boolean = false

  constructor(private contactService: ContactService) { }

  ngOnInit(): void {
  }

  onMouseEnter() {
    this.displayButtons = true;
  }

  onMouseLeave() {
    this.displayButtons = false;
  }

  onApproval(approve: boolean) {
    this.contactService.approveContactForFurtherCommunication(this.contact.contact_id, approve).subscribe();
  }
}
