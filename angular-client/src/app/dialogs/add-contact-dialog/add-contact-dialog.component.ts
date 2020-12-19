import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AddContactDialogData } from './add-contact-dialog-data';

@Component({
  templateUrl: './add-contact-dialog.component.html',
  styleUrls: ['./add-contact-dialog.component.css']
})
export class AddContactDialogComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<AddContactDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: AddContactDialogData) { }

  ngOnInit(): void {
  }

  onCancelClick() {
    this.dialogRef.close();
  }

}
