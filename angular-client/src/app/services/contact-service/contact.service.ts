import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ContactDto } from 'src/app/data-transfer/contact-dto';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { BaseService } from '../base-service/base.service';

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  api_prefix = '/contacts/'
  contacts_address: string

  constructor(private base: BaseService, private http: HttpClient) { 
    this.contacts_address = this.base.api_address + this.api_prefix;
  }

  getAllContacts(): Observable<ContactDto[]> {
    return this.http.get<ContactDto[]>(this.contacts_address);
  }

  getContactByid(id: string): Observable<ContactDto> {
    return this.http.get<ContactDto>(this.contacts_address + id);
  }

  addContact(contactDto: ContactDto): Observable<ContactDto> {
    return this.http.post<ContactDto>(this.contacts_address, contactDto);
  }

  changeName(contactId: string, newName: string): Observable<ContactDto> {
    return this.http.patch<ContactDto>(this.contacts_address + contactId + '?name=' + newName, null);
  }

  removeContact(contactId: string) {
    return this.http.delete(this.contacts_address + contactId);
  }

  getMessagesForContact(contactId: string): Observable<MessageDto[]> {
    return this.http.get<MessageDto[]>(this.contacts_address + contactId + '/messages');
  }

  approveContactForFurtherCommunication(contactId: string, isApproved: boolean) {
    return this.http.patch(this.contacts_address + contactId + '/approval?approved=' + isApproved, null);
  }
}
