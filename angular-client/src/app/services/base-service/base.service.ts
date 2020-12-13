import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BaseService {
  api_address = 'http://localhost:5000/api'

  constructor() { }
}
