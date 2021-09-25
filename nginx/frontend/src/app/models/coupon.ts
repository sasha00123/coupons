import {Ctype} from './ctype';
import {Category} from './category';
import {Interest} from './interest';

export class Coupon {
  id: number;
  name: string;
  description: string;
  ctype: Ctype;
  category: Category;
  campaign: number;
  outlets: number[];
  deal: string;
  image: string;
  TC: string;
  amount: number;
  code: string;
  start: Date;
  end: Date;
  advertisement: boolean;
  active: boolean;
  published: boolean;
  interests: Interest[];
}
