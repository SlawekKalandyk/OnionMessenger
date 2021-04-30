import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CurrentContactService } from './services/current-contact-service/current-contact.service';
import { SocketService } from './services/socket-service/socket.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  received: string = ''
  isAnyContactActive: boolean = false
  isHiddenServiceActive: boolean = false

  constructor(private http: HttpClient, private currentContactService: CurrentContactService, private socketService: SocketService) {
  }

  ngOnInit() {
    this.currentContactService.currentContact.subscribe(response => this.isAnyContactActive = response != undefined);
    this.socketService.getHiddenServiceStart().subscribe(_ => {
      this.isHiddenServiceActive = true;
      console.log('Hidden Service has started');
      this.http.get<string>('http://127.0.0.1:5000/api/contacts').subscribe(response => {
      this.received = response;
    });
    });
  }
}
