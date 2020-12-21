import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AddContactNameOnApproveDialogComponent } from 'src/app/dialogs/add-contact-name-on-approve-dialog/add-contact-name-on-approve-dialog.component';
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

  constructor(public dialog: MatDialog, private contactService: ContactService) { }

  ngOnInit(): void {
  }

  onMouseEnter() {
    this.displayButtons = true;
  }

  onMouseLeave() {
    this.displayButtons = false;
  }

  onApproval(approve: boolean) {
    const dialogRef = this.dialog.open(AddContactNameOnApproveDialogComponent, {
      width: '600px',
      data: { name: ''}
    });
    dialogRef.afterClosed().subscribe(result => {
      this.contactService.changeName(this.contact.contact_id, result.name).subscribe(_ => {
        this.contactService.approveContactForFurtherCommunication(this.contact.contact_id, approve).subscribe();
      })
    });
  }
}
