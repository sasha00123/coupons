import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {LoginComponent} from './login/login.component';
import {HomeComponent} from './home/home.component';
import {CookieService} from 'ngx-cookie-service';
import {AuthService} from './auth/auth.service';
import {AuthGuard} from './auth/auth.guard';
import {AppRoutingModule} from './app-routing/app-routing.module';
import {FormsModule} from '@angular/forms';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {CreateCampaignComponent} from './create-campaign/create-campaign.component';
import {OwlDateTimeModule, OwlNativeDateTimeModule} from 'ng-pick-datetime';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {CreateCouponComponent} from './create-coupon/create-coupon.component';
import {NgSelectModule} from '@ng-select/ng-select';
import {ListCampaignsComponent} from './list-campaigns/list-campaigns.component';
import {ListCouponsComponent} from './list-coupons/list-coupons.component';
import {TokenInterceptor} from './http.interceptor';
import {FilterCampaignsPipe} from './filter-campaigns.pipe';
import {EditCampaignComponent} from './edit-campaign/edit-campaign.component';
import {EditCouponComponent} from './edit-coupon/edit-coupon.component';
import {FilterCouponsPipe} from './filter-coupons.pipe';
import {EditOrganizationComponent} from './edit-organization/edit-organization.component';
import {AlertsComponent} from './alerts/alerts.component';
import {LoadingComponent} from './loading/loading.component';
import {CreateOutletComponent} from './create-outlet/create-outlet.component';
import {EditOutletComponent} from './edit-outlet/edit-outlet.component';
import {ListOutletsComponent} from './list-outlets/list-outlets.component';
import { RegisterComponent } from './register/register.component';
import { BackComponent } from './back/back.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    HomeComponent,
    CreateCampaignComponent,
    CreateCouponComponent,
    ListCampaignsComponent,
    ListCouponsComponent,
    FilterCampaignsPipe,
    EditCampaignComponent,
    EditCouponComponent,
    FilterCouponsPipe,
    EditOrganizationComponent,
    AlertsComponent,
    LoadingComponent,
    CreateOutletComponent,
    EditOutletComponent,
    ListOutletsComponent,
    RegisterComponent,
    BackComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgSelectModule,
    FormsModule
  ],
  providers: [CookieService, AuthService, AuthGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: TokenInterceptor,
      multi: true
    }],
  bootstrap: [AppComponent]
})
export class AppModule {
}
