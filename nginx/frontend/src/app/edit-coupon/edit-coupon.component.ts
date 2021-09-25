import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {Category} from '../models/category';
import {Interest} from '../models/interest';
import {Outlet} from '../models/outlet';
import {Campaign} from '../models/campaign';
import {Ctype} from '../models/ctype';
import {DataService} from '../data.service';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-edit-coupon',
  templateUrl: '../forms/coupon.form.html',
  styleUrls: ['./edit-coupon.component.css']
})
export class EditCouponComponent implements OnInit {
  id: number;
  name: string;
  description: string;
  deal: string;
  image: File;
  imageurl: string;
  TC: string;
  amount: number;
  code: string;
  start: Date;
  end: Date;
  advertisement: boolean;
  active: boolean;
  published: boolean;
  infinite: boolean;

  selected = {
    type: 1,
    category: 0,
    campaign: 0,
    interests: [],
    outlets: []
  };

  dealFields = {
    sale: 0,

    buy: 0,
    next: '',

    amount: 0,
    cost: 0,
    save: 0
  };

  editing = true;
  imageIsValid = true;

  types$: Observable<Ctype>;
  categories$: Observable<Category>;
  interests$: Observable<Interest>;
  campaigns: Campaign[];
  outlets: Outlet[];

  loading = true;

  verified = false;

  constructor(private data: DataService, private route: ActivatedRoute) {
  }

  handleFileInput(files: FileList) {
    this.image = files.item(0);
    this.imageIsValid = this.image.size / 1024.0 / 1024.0 <= 1;
  }

  submit() {
    try {
      this.send();
    } catch (e) {
      console.log(e);
    }
  }

  generateCode() {
    this.code = this.data.getRandomString();
  }

  send() {
    this.loading = true;
    switch (this.selected.type) {
      case 1: {
        this.deal = JSON.stringify({'sale': this.dealFields.sale});
        break;
      }
      case 2: {
        this.deal = JSON.stringify({'buy': this.dealFields.buy, 'next': this.dealFields.next});
        break;
      }
      case 3: {
        this.deal = JSON.stringify({
          'amount': this.dealFields.amount,
          'cost': this.dealFields.cost,
          'save': this.dealFields.save
        });
        break;
      }
    }
    const data = {
      'name': this.name,
      'description': this.description,
      'deal': this.deal,
      'TC': this.TC,
      'code': this.code,
      'image': this.image,
      'amount': this.infinite ? -1 : this.amount,
      'start': this.start.toISOString(),
      'end': this.end.toISOString(),
      'advertisement': this.advertisement,
      'published': this.published,
      'active': this.active,
      'infinite': this.infinite,
      'ctype': this.selected.type,
      'category': this.selected.category,
      'campaign': this.selected.campaign,
      'interests': this.selected.interests,
      'outlets': this.selected.outlets
    };

    this.data.editCoupon(this.id, data).subscribe(d => {
      this.updateCouponData();
    }, err => {
      console.log(err);
    });
  }

  updateCouponData() {
    this.data.getCoupon(this.route.snapshot.params.id).subscribe(coupon => {
      this.id = coupon.id;
      this.name = coupon.name;
      this.description = coupon.description;
      this.imageurl = coupon.image;
      this.TC = coupon.TC;
      this.amount = coupon.amount;
      this.code = coupon.code;
      this.start = new Date(coupon.start);
      this.end = new Date(coupon.end);
      this.advertisement = coupon.advertisement;
      this.active = coupon.active;
      this.published = coupon.published;
      this.infinite = coupon.amount === -1;

      this.selected.type = coupon.ctype.id;
      this.selected.campaign = coupon.campaign;
      this.selected.outlets = coupon.outlets;
      this.selected.interests = coupon.interests.map(interest => interest.id);
      this.selected.category = coupon.category.id;

      const deal = JSON.parse(coupon.deal);
      Object.keys(this.dealFields).forEach(key => {
        if (deal.hasOwnProperty(key)) {
          this.dealFields[key] = deal[key];
        }
      });
      this.loading = false;
    });
  }

  ngOnInit() {
    this.interests$ = this.data.getInterests();
    this.categories$ = this.data.getCategories();
    this.types$ = this.data.getTypes();
    this.data.getVendorData().subscribe(data => {
      this.campaigns = data.campaigns;
      this.outlets = data.outlets;
      if (data.organization !== null) {
        this.verified = data.organization.verified;
      }
    });
    this.updateCouponData();
  }

  selectAll() {
    this.selected.outlets = this.outlets.map(outlet => outlet.id);
  }

  unselectAll() {
    this.selected.outlets = [];
  }

}
