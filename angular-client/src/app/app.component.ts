import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  received: string = ''

  constructor(private http: HttpClient) {
  }

  ngOnInit() {
    this.http.get<string>('http://127.0.0.1:5000/api/contacts').subscribe(response => {
      console.log(response);
      this.received = response;
    });
  }
}
