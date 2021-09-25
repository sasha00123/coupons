import {Component, OnInit} from '@angular/core';
import {DataService} from '../data.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-create-campaign',
  templateUrl: '../forms/campaign.form.html',
  styleUrls: ['./create-campaign.component.css']
})
export class CreateCampaignComponent implements OnInit {
  name: string;
  start: Date;
  end: Date;
  active: boolean;
  loading = false;
  verified = false;

  constructor(private data: DataService, private router: Router) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      if (data.organization !== null) {
        this.verified = data.verified;
      }
    });
  }

  save() {
    this.loading = true;
    this.data.getVendorData().subscribe(data => {
      this.data.createCampaign({
        'name': this.name,
        'start': this.start.toISOString(),
        'end': this.end.toISOString(),
        'organization': data.organization.id,
        'active': this.active
      }).subscribe(
        campaign => this.router.navigateByUrl('/?created=campaign'),
        error => console.log(error)
      );
    });
  }
}
