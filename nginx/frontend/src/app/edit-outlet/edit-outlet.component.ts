import {Component, OnInit} from '@angular/core';
import {DataService} from '../data.service';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-edit-outlet',
  templateUrl: '../forms/outlet.form.html',
  styleUrls: ['./edit-outlet.component.css']
})
export class EditOutletComponent implements OnInit {
  id: number;
  name: string;
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  loading = true;
  verified = false;

  constructor(private data: DataService, private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.data.getOutlet(this.route.snapshot.params.id).subscribe(data => {
      this.id = data.id;
      this.name = data.name;
      this.description = data.description;
      this.address = data.address;
      this.latitude = data.latitude;
      this.longitude = data.longitude;
      this.loading = false;
    });
    this.data.getVendorData().subscribe(data => {
      if (data.organization !== null) {
        this.verified = data.organization.verified;
      }
    });
  }

  save() {
    this.loading = true;
    this.data.getVendorData().subscribe(vendor => {
      this.data.editOutlet(this.id, {
        'name': this.name,
        'description': this.description,
        'address': this.address,
        'latitude': this.latitude,
        'longitude': this.longitude,
        'organization': vendor.organization.id
      }).subscribe(data => {
        this.loading = false;
      });
    });
  }
}
