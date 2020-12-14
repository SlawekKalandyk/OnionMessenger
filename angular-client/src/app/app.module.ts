import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

import { ContactsNavComponent } from './components/contacts-nav/contacts-nav.component';
import { ContactCardComponent } from './components/contact-card/contact-card.component';
import { ChatComponent } from './components/chat/chat.component';
import { MessageCardComponent } from './components/message-card/message-card.component';

@NgModule({
  declarations: [
    AppComponent,
    ContactsNavComponent,
    ContactCardComponent,
    ChatComponent,
    MessageCardComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatSidenavModule,
    MatListModule,
    MatButtonModule,
    MatCardModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
