import {Pipe, PipeTransform} from '@angular/core';
import {Campaign} from './models/campaign';

@Pipe({
  name: 'filterCampaigns'
})
export class FilterCampaignsPipe implements PipeTransform {

  transform(campaigns: Campaign[], filter: string): Campaign[] {
    switch (filter) {
      case 'active': {
        return campaigns.filter(campaign => campaign.active);
      }
      case 'inactive': {
        return campaigns.filter(campaign => !campaign.active);
      }
      case 'used': {
        return campaigns.filter(campaign => campaign.end < new Date());
      }
      default: {
        return campaigns;
      }
    }
  }

}
