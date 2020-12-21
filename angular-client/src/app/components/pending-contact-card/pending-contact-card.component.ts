import { Component, Input, OnInit } from '@angular/core';
import { Contact } from 'src/app/model/contact';

@Component({
  selector: 'app-pending-contact-card',
  templateUrl: './pending-contact-card.component.html',
  styleUrls: ['./pending-contact-card.component.css']
})
export class PendingContactCardComponent implements OnInit {
  @Input() contact!: Contact;
  displayButtons: boolean = false

  constructor() { }

  ngOnInit(): void {
  }

  onMouseEnter() {
    this.displayButtons = true;
  }

  onMouseLeave() {
    this.displayButtons = false;
  }

  onApproval(approve: boolean) {

  }
}
