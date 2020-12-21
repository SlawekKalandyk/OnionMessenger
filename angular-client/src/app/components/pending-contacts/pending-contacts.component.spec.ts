import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PendingContactsComponent } from './pending-contacts.component';

describe('PendingContactsComponent', () => {
  let component: PendingContactsComponent;
  let fixture: ComponentFixture<PendingContactsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PendingContactsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PendingContactsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
