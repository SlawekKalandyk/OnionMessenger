import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import * as socketio from 'socket.io-client';
import { ContactDto } from 'src/app/data-transfer/contact-dto';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { Contact } from 'src/app/model/contact';
import { Message } from 'src/app/model/message';
import { environment } from 'src/environments/environment';
import { DtoMappingService } from '../dto-mapping-service/dto-mapping.service';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: any;

  constructor(private mappingService: DtoMappingService) {
    this.socket = socketio.io(environment.socket_url);
  }

  getMessages(): Observable<Message> {
    return new Observable(observer => {
      this.socket.on('message', (messageDto: MessageDto) => {
        let message = this.mappingService.mapMessageDtoToMessage(messageDto);
        observer.next(message);
      });
    });
  }

  getNewContactPendingInterlocutorApproval(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('new-contact-pending-interlocutor-approval', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getNewContactPendingSelfApproval(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('new-contact-pending-self-approval', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getNewlyApprovedContact(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('approved-contact', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getNewlyNotApprovedContact(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('not-approved-contact', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getReceivedContactApproval(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('received-approved-contact', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getContactOnline(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('contact-online', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getContactOffline(): Observable<Contact> {
    return new Observable(observer => {
      this.socket.on('contact-offline', (contactDto: ContactDto) => {
        let contact = this.mappingService.mapContactDtoToContact(contactDto);
        observer.next(contact);
      });
    });
  }

  getHiddenServiceStart(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('hidden-service-start', () => {
        observer.next();
      });
    });
  }
}
