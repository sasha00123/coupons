import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {Ctype} from '../models/ctype';
import {Category} from '../models/category';
import {DataService} from '../data.service';
import {Interest} from '../models/interest';
import {Campaign} from '../models/campaign';
import {Outlet} from '../models/outlet';
import {Router} from '@angular/router';

@Component({
  selector: 'app-create-coupon',
  templateUrl: '../forms/coupon.form.html',
  styleUrls: ['./create-coupon.component.css']
})
export class CreateCouponComponent implements OnInit {
  name: string;
  description: string;
  image: File;
  imageurl: string;
  TC: string;
  deal: string;
  amount: number;
  code: string;
  start: Date;
  end: Date;
  advertisement = false;
  active = false;
  published = false;
  infinite = false;

  dealFields = {
    sale: 0,

    buy: 0,
    next: '',

    amount: 0,
    cost: 0,
    save: 0
  };

  selected = {
    type: 1,
    category: null,
    campaign: null,
    interests: [],
    outlets: []
  };

  editing = false;
  imageIsValid = false;

  types$: Observable<Ctype>;
  categories$: Observable<Category>;
  interests$: Observable<Interest>;
  campaigns: Campaign[];
  outlets: Outlet[];

  loading = false;
  verified = false;

  constructor(private data: DataService, private router: Router) {
  }

  handleFileInput(files: FileList) {
    this.image = files.item(0);
    this.imageIsValid = this.image.size / 1024.0 / 1024.0 <= 1;
  }

  generateCode() {
    this.code = this.data.getRandomString();
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
  }

  selectAll() {
    this.selected.outlets = this.outlets.map(outlet => outlet.id);
  }

  unselectAll() {
    this.selected.outlets = [];
  }

  submit() {
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
    this.data.createCoupon({
      'name': this.name,
      'description': this.description,
      'deal': this.deal,
      'image': this.image,
      'TC': this.TC,
      'code': this.code,
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
    }).subscribe(data => {
      this.loading = false;
      this.router.navigateByUrl('/?created=coupon');
    }, err => {
      console.log(err);
    });
  }
}
