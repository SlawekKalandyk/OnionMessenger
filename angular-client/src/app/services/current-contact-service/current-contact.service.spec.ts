import { TestBed } from '@angular/core/testing';

import { CurrentContactService } from './current-contact.service';

describe('CurrentContactService', () => {
  let service: CurrentContactService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CurrentContactService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
