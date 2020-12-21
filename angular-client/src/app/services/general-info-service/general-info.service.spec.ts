import { TestBed } from '@angular/core/testing';

import { GeneralInfoService } from './general-info.service';

describe('GeneralInfoService', () => {
  let service: GeneralInfoService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GeneralInfoService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
