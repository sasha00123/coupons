import {Component, OnInit} from '@angular/core';
import {DataService} from '../data.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-create-outlet',
  templateUrl: '../forms/outlet.form.html',
  styleUrls: ['./create-outlet.component.css']
})
export class CreateOutletComponent implements OnInit {
  name: string;
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  loading = false;
  verified = false;

  constructor(private data: DataService, private router: Router) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      if (data.organization !== null) {
        this.verified = data.organization.verified;
      }
    });
  }

  save() {
    this.loading = true;
    this.data.getVendorData().subscribe(vendor => {
      this.data.createOutlet({
        'name': this.name,
        'description': this.description,
        'address': this.address,
        'latitude': this.latitude,
        'longitude': this.longitude,
        'organization': vendor.organization.id
      }).subscribe(data => this.router.navigateByUrl('/?created=outlet'));
    });
  }
}
