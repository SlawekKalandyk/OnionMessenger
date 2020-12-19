import { DatePipe } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { ContentType, Message } from 'src/app/model/message';

@Component({
  selector: 'app-message-card',
  templateUrl: './message-card.component.html',
  styleUrls: ['./message-card.component.css'],
  providers: [DatePipe]
})
export class MessageCardComponent implements OnInit {
  @Input() message!: Message
  content: any
  timestamp: any

  constructor(public datePipe: DatePipe) { }

  ngOnInit(): void {
    if(this.message.content_type == ContentType.STRING) {
      this.content = this.message.content;
    }
    this.timestamp = this.datePipe.transform(this.message.timestamp, 'yyyy-MM-dd hh:mm')
  }

}
