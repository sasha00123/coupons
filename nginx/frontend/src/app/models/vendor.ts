import {Coupon} from './coupon';
import {Campaign} from './campaign';
import {Organization} from './organization';
import {Outlet} from './outlet';

export class Vendor {
  restricted: boolean;
  verified: boolean;
  email: string;
  organization: Organization;
  campaigns: Campaign[];
  coupons: Coupon[];
  outlets: Outlet[];
}
