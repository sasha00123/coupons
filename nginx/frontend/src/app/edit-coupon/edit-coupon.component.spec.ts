import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditCouponComponent } from './edit-coupon.component';

describe('EditCouponComponent', () => {
  let component: EditCouponComponent;
  let fixture: ComponentFixture<EditCouponComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditCouponComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditCouponComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
