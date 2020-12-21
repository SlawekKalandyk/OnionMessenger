import { Component, OnInit } from '@angular/core';
import { GeneralInfoService } from 'src/app/services/general-info-service/general-info.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css']
})
export class UserSettingsComponent implements OnInit {
  serviceId!: string;

  constructor(private generalInfo: GeneralInfoService) { }

  ngOnInit(): void {
    this.generalInfo.getHiddenServiceAddress().subscribe(serviceId => this.serviceId = serviceId);
  }

}
