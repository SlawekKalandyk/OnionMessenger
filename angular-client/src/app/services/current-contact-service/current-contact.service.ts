import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';
import { Contact } from 'src/app/data-transfer/contact';

@Injectable({
  providedIn: 'root'
})
export class CurrentContactService {
  private currentContactSource = new ReplaySubject<Contact>(1);
  public _currentContact: Observable<Contact> = this.currentContactSource.asObservable();

  constructor() { }

  set currentContact(contact: Observable<Contact>) {
    contact.subscribe(response => this.currentContactSource.next(response));
  }

  get currentContact() {
    return this._currentContact;
  }
}
