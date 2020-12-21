import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MessageDto } from 'src/app/data-transfer/message-dto';
import { BaseService } from 'src/app/services/base-service/base.service';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  api_prefix = '/messages/'
  messages_address: string

  constructor(private base: BaseService, private http: HttpClient) { 
    this.messages_address = this.base.api_address + this.api_prefix;
  }

  sendMessage(messageDto: MessageDto) {
    return this.http.post(this.messages_address, messageDto);
  }
}
