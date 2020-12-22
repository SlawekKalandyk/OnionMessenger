import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import * as socketio from 'socket.io-client';
import { ContactDto } from 'src/app/data-transfer/contact-dto';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: any;

  constructor() {
    this.socket = socketio.io(environment.socket_url);
  }

  getMessages(): Observable<MessageDto> {
    return new Observable(observer => {
      this.socket.on('message', (message: MessageDto) => {
        observer.next(message);
      });
    });
  }

  getContacts(): Observable<ContactDto> {
    return new Observable(observer => {
      this.socket.on('contact', (contact: ContactDto) => {
        observer.next(contact);
      });
    });
  }

  getHiddenServiceStart(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('hidden-service-start', (a: any) => {
        observer.next(a);
      });
    });
  }
}
