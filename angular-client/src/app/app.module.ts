import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';

import { ContactsNavComponent } from './components/contacts-nav/contacts-nav.component';
import { ContactCardComponent } from './components/contact-card/contact-card.component';
import { ChatComponent } from './components/chat/chat.component';
import { MessageCardComponent } from './components/message-card/message-card.component';
import { ChatBoxComponent } from './components/chat-box/chat-box.component';
import { AddContactDialogComponent } from './dialogs/add-contact-dialog/add-contact-dialog.component';
import { MessageTimestampSortPipe } from './pipes/message-timestamp-sort/message-timestamp-sort.pipe';
import { UserSettingsComponent } from './components/user-settings/user-settings.component';
import { PendingContactsComponent } from './components/pending-contacts/pending-contacts.component';
import { PendingContactCardComponent } from './components/pending-contact-card/pending-contact-card.component';
import { AddContactNameOnApproveDialogComponent } from './dialogs/add-contact-name-on-approve-dialog/add-contact-name-on-approve-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    ContactsNavComponent,
    ContactCardComponent,
    ChatComponent,
    MessageCardComponent,
    ChatBoxComponent,
    AddContactDialogComponent,
    MessageTimestampSortPipe,
    UserSettingsComponent,
    PendingContactsComponent,
    PendingContactCardComponent,
    AddContactNameOnApproveDialogComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    FormsModule,
    MatSidenavModule,
    MatListModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatTabsModule,
    MatDividerModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
