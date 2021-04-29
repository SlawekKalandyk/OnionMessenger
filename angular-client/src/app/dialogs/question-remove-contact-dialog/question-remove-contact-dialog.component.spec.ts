import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QuestionRemoveContactDialogComponent } from './question-remove-contact-dialog.component';

describe('QuestionRemoveContactDialogComponent', () => {
  let component: QuestionRemoveContactDialogComponent;
  let fixture: ComponentFixture<QuestionRemoveContactDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ QuestionRemoveContactDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(QuestionRemoveContactDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
