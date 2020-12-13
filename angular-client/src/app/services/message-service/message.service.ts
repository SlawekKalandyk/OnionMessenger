import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Message } from 'src/app/data-transfer/message';
import { BaseService } from '../base-service/base.service';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  api_prefix = '/messages/'
  messages_address: string

  constructor(private base: BaseService, private http: HttpClient) { 
    this.messages_address = this.base.api_address + this.api_prefix
  }

  sendMessage(message: Message) {
    return this.http.post(this.messages_address, message)
  }
}
