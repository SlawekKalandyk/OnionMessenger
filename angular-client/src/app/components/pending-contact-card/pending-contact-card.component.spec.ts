import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PendingContactCardComponent } from './pending-contact-card.component';

describe('PendingContactCardComponent', () => {
  let component: PendingContactCardComponent;
  let fixture: ComponentFixture<PendingContactCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PendingContactCardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PendingContactCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
