import { TestBed } from '@angular/core/testing';

import { DtoMappingService } from './dto-mapping.service';

describe('DtoMappingService', () => {
  let service: DtoMappingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DtoMappingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
