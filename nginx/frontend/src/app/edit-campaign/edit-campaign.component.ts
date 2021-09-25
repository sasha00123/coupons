import {Component, OnInit} from '@angular/core';
import {DataService} from '../data.service';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-edit-campaign',
  templateUrl: '../forms/campaign.form.html',
  styleUrls: ['./edit-campaign.component.css']
})
export class EditCampaignComponent implements OnInit {
  id: number;
  name: string;
  start: Date;
  end: Date;
  active: boolean;
  loading = true;
  verified = false;

  constructor(private data: DataService, private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      if (data.organization !== null) {
        this.verified = data.organization.verified;
      }
    });
    this.data.getCampaign(this.route.snapshot.params.id).subscribe(data => {
      this.id = data.id;
      this.name = data.name;
      this.start = new Date(data.start);
      this.end = new Date(data.end);
      this.active = data.active;
      this.loading = false;
    });
  }

  save() {
    this.loading = true;
    this.data.editCampaign(this.id, {
      'name': this.name,
      'start': this.start.toISOString(),
      'end': this.end.toISOString(),
      'active': this.active
    }).subscribe(data => {
      this.loading = false;
    });
  }

}
