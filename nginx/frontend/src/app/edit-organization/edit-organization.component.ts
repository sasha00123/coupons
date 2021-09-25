import {Component, OnInit} from '@angular/core';
import {DataService} from '../data.service';
import {Organization} from '../models/organization';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';

@Component({
  selector: 'app-edit-organization',
  templateUrl: '../forms/organization.form.html',
  styleUrls: ['./edit-organization.component.css']
})
export class EditOrganizationComponent implements OnInit {
  id = 0;
  name = '';
  address = '';
  created: boolean;
  loading = true;
  obs: Observable<Organization>;
  updatedData = {};
  verified = false;
  alreadyVerified = false;

  constructor(private data: DataService, private router: Router) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      if (data.organization !== null) {
        this.created = true;
        this.id = data.organization.id;
        this.name = data.organization.name;
        this.address = data.organization.address;
	this.alreadyVerified = data.organization.verified;
      } else {
        this.created = false;
      }
      this.verified = data.verified;
      this.loading = false;
    });
  }

  save() {
    this.loading = true;
    this.updatedData = {
      'name': this.name,
      'address': this.address
    };
    if (this.created) {
      this.obs = this.data.editOrganization(this.id, this.updatedData);
    } else {
      this.obs = this.data.createOrganization(this.updatedData);
    }
    this.obs.subscribe(data => {
      if (this.created === false) {
        this.router.navigateByUrl('/?created=organization');
      }
      this.loading = false;
    });
  }
}
