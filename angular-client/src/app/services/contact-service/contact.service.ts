import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Contact } from 'src/app/data-transfer/contact';
import { Message } from 'src/app/data-transfer/message';
import { BaseService } from '../base-service/base.service';

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  api_prefix = '/contacts/'
  contacts_address: string

  constructor(private base: BaseService, private http: HttpClient) { 
    this.contacts_address = this.base.api_address + this.api_prefix
  }

  getAllContacts(): Observable<Contact[]> {
    return this.http.get<Contact[]>(this.contacts_address)
  }

  getContactByid(id: string): Observable<Contact> {
    return this.http.get<Contact>(this.contacts_address + id)
  }

  addContact(contact: Contact): Observable<Contact> {
    return this.http.post<Contact>(this.contacts_address, contact)
  }

  changeName(contactId: string, newName: string): Observable<Contact> {
    return this.http.patch<Contact>(this.contacts_address + contactId + '?name=' + newName, null)
  }

  removeContact(contactId: string) {
    return this.http.delete(this.contacts_address + contactId)
  }

  getMessagesForContact(contactId: string): Observable<Message[]> {
    return this.http.get<Message[]>(this.contacts_address + contactId + '/messages')
  }

  approveContactForFurtherCommunication(contactId: string, isApproved: boolean) {
    return this.http.patch(this.contacts_address + contactId + '/approval?approved=' + isApproved, null)
  }
}
