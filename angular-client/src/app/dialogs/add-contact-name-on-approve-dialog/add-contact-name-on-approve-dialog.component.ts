import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AddContactNameOnApproveDialogData } from './add-contact-name-on-approve-dialog-data';

@Component({
  templateUrl: './add-contact-name-on-approve-dialog.component.html',
  styleUrls: ['./add-contact-name-on-approve-dialog.component.css']
})
export class AddContactNameOnApproveDialogComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<AddContactNameOnApproveDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: AddContactNameOnApproveDialogData) { }

  ngOnInit(): void {
  }

  onCancelClick() {
    this.dialogRef.close();
  }
}
