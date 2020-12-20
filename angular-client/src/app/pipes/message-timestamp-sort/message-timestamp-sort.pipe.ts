import { Pipe, PipeTransform } from '@angular/core';
import { Message } from 'src/app/model/message';

@Pipe({
  name: 'messageTimestampSort'
})
export class MessageTimestampSortPipe implements PipeTransform {

  transform(array: Message[]): Message[] {
    return array.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

}
