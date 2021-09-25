import {Component, OnInit} from '@angular/core';
import {Vendor} from '../models/vendor';
import {DataService} from '../data.service';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-alerts',
  templateUrl: './alerts.component.html',
  styleUrls: ['./alerts.component.css']
})
export class AlertsComponent implements OnInit {
  vendor: Vendor;
  alertsLoaded = false;
  created = '';

  constructor(private data: DataService, private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
        this.vendor = data;
        this.route.queryParams.subscribe(params => {
          this.created = params['created'];
          this.alertsLoaded = true;
        });
      }
    );
  }

}
