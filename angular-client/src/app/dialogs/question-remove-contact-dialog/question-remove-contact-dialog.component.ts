import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ContactService } from 'src/app/services/contact-service/contact.service';
import { QuestionRemoveContactDialogData } from './question-remove-contact-dialog-data';

@Component({
  templateUrl: './question-remove-contact-dialog.component.html',
  styleUrls: ['./question-remove-contact-dialog.component.css']
})
export class QuestionRemoveContactDialogComponent implements OnInit {
  enteredContactId: string = '';
  enteredContactIdError: boolean = false;

  constructor(public dialogRef: MatDialogRef<QuestionRemoveContactDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: QuestionRemoveContactDialogData, 
              private contactService: ContactService) { }

  ngOnInit(): void {
  }

  onCancelClick() {
    this.dialogRef.close();
  }

  onConfirmClick() {
    if (this.enteredContactId == this.data.contactId.substr(0, 8)) {
      this.contactService.removeContact(this.data.contactId).subscribe();
      this.dialogRef.close();
    } else {
      this.enteredContactIdError = true;
    }
  }
}
