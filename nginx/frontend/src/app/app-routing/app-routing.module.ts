import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from '../home/home.component';
import {AuthGuard} from '../auth/auth.guard';
import {LoginComponent} from '../login/login.component';
import {CreateCampaignComponent} from '../create-campaign/create-campaign.component';
import {CreateCouponComponent} from '../create-coupon/create-coupon.component';
import {ListCampaignsComponent} from '../list-campaigns/list-campaigns.component';
import {EditCampaignComponent} from '../edit-campaign/edit-campaign.component';
import {EditCouponComponent} from '../edit-coupon/edit-coupon.component';
import {ListCouponsComponent} from '../list-coupons/list-coupons.component';
import {EditOrganizationComponent} from '../edit-organization/edit-organization.component';
import {CreateOutletComponent} from '../create-outlet/create-outlet.component';
import {ListOutletsComponent} from '../list-outlets/list-outlets.component';
import {EditOutletComponent} from '../edit-outlet/edit-outlet.component';
import {RegisterComponent} from '../register/register.component';

const routes: Routes = [
  {
    path: '',
    canActivate: [AuthGuard],
    children: [
      {
        path: '',
        component: HomeComponent,
      },
      {
        path: 'campaigns',
        children: [
          {
            path: 'create',
            component: CreateCampaignComponent
          },
          {
            path: 'list/:filter',
            component: ListCampaignsComponent
          },
          {
            path: 'edit/:id',
            component: EditCampaignComponent
          }
        ]
      },
      {
        path: 'coupons',
        children: [
          {
            path: 'create',
            component: CreateCouponComponent
          },
          {
            path: 'list/:filter',
            component: ListCouponsComponent
          },
          {
            path: 'edit/:id',
            component: EditCouponComponent
          }
        ]
      },
      {
        path: 'organization',
        component: EditOrganizationComponent
      },
      {
        path: 'outlets',
        children: [
          {
            path: 'create',
            component: CreateOutletComponent
          },
          {
            path: 'list',
            component: ListOutletsComponent
          },
          {
            path: 'edit/:id',
            component: EditOutletComponent
          }
        ]
      }
    ]
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
