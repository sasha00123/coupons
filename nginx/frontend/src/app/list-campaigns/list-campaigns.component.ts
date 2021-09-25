import {Component, OnInit} from '@angular/core';
import {Vendor} from '../models/vendor';
import {DataService} from '../data.service';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-list-campaigns',
  templateUrl: './list-campaigns.component.html',
  styleUrls: ['./list-campaigns.component.css']
})
export class ListCampaignsComponent implements OnInit {
  loading = true;
  vendor: Vendor;
  filter: string;
  disabled = true;

  constructor(private data: DataService, private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(vendor => {
      this.vendor = vendor;
      if (vendor.organization !== null) {
        this.disabled = !vendor.organization.verified;
      }
      this.loading = false;
    });
    this.filter = this.route.snapshot.params.filter || '';
  }

}
