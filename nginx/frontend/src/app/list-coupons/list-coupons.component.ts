import {Component, OnInit} from '@angular/core';
import {Coupon} from '../models/coupon';
import {DataService} from '../data.service';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-list-coupons',
  templateUrl: './list-coupons.component.html',
  styleUrls: ['./list-coupons.component.css']
})
export class ListCouponsComponent implements OnInit {
  loading = true;
  coupons: Coupon[];
  filter: string;
  disabled = true;

  constructor(private data: DataService, private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      this.coupons = data.coupons;
      if (data.organization !== null) {
        this.disabled = !data.organization.verified;
      }
      this.loading = false;
      this.filter = this.route.snapshot.params.filter || '';
    });
  }

}
