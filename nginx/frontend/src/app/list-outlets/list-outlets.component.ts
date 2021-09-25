import {Component, OnInit} from '@angular/core';
import {DataService} from '../data.service';
import {Vendor} from '../models/vendor';

@Component({
  selector: 'app-list-outlets',
  templateUrl: './list-outlets.component.html',
  styleUrls: ['./list-outlets.component.css']
})
export class ListOutletsComponent implements OnInit {
  vendor: Vendor;
  loading = true;
  disabled = true;

  constructor(private data: DataService) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      this.vendor = data;
      if (data.organization !== null) {
        this.disabled = !data.organization.verified;
      }
      this.loading = false;
    });
  }

}
