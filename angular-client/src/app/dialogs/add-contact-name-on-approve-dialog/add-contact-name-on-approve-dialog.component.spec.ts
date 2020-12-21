import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddContactNameOnApproveDialogComponent } from './add-contact-name-on-approve-dialog.component';

describe('AddContactNameOnApproveDialogComponent', () => {
  let component: AddContactNameOnApproveDialogComponent;
  let fixture: ComponentFixture<AddContactNameOnApproveDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddContactNameOnApproveDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AddContactNameOnApproveDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
