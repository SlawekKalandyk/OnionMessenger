import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BaseService } from 'src/app/services/base-service/base.service';

@Injectable({
  providedIn: 'root'
})
export class GeneralInfoService {
  api_prefix = '/info/';
  info_address: string
  constructor(private base: BaseService, private http: HttpClient) {
    this.info_address = this.base.api_address + this.api_prefix;
  }

  getHiddenServiceAddress() {
    return this.http.get<string>(this.info_address + 'serviceId');
  }
}
