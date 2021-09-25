import {Pipe, PipeTransform} from '@angular/core';
import {Coupon} from './models/coupon';

@Pipe({
  name: 'filterCoupons'
})
export class FilterCouponsPipe implements PipeTransform {

  transform(coupons: Coupon[], filter: string) {
    switch (filter) {
      case 'active': {
        return coupons.filter(coupon => coupon.active);
      }
      case 'inactive': {
        return coupons.filter(coupon => !coupon.active);
      }
      case 'used': {
        return coupons.filter(coupon => coupon.end < new Date());
      }
      default: {
        return coupons;
      }
    }
  }

}
