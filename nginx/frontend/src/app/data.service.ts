import {Injectable} from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {catchError, retry} from 'rxjs/operators';
import {AuthService} from './auth/auth.service';
import {Router} from '@angular/router';
import {Observable, throwError} from 'rxjs';
import {Vendor} from './models/vendor';
import {environment} from '../environments/environment';
import {Campaign} from './models/campaign';
import {CookieService} from 'ngx-cookie-service';
import {Interest} from './models/interest';
import {Category} from './models/category';
import {Ctype} from './models/ctype';
import {Organization} from './models/organization';
import {Coupon} from './models/coupon';
import {Outlet} from './models/outlet';
import {isArray} from 'util';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  constructor(private authService: AuthService, private router: Router,
              private http: HttpClient, private cookie: CookieService) {
  }

  createCampaign(data: object): Observable<Campaign> {
    return this.http.post<Campaign>(environment.apiUrl + 'campaigns', data).pipe(
      catchError(err => this.handleError(err))
    );
  }

  getVendorData(): Observable<Vendor> {
    return this.http.get<Vendor>(environment.apiUrl + 'accounts/vendor').pipe(
      catchError(err => this.handleError(err))
    );
  }

  createOrganization(data: object): Observable<Organization> {
    return this.http.post<Organization>(environment.apiUrl + 'organizations', data).pipe(
      catchError(err => this.handleError(err))
    );
  }

  editOrganization(id: number, data: object) {
    return this.http.patch<Organization>(environment.apiUrl + `organizations/${id}`, data).pipe(
      catchError(err => this.handleError(err))
    );
  }

  getCampaign(id: number): Observable<Campaign> {
    return this.http.get<Campaign>(environment.apiUrl + `campaigns/${id}`).pipe(
      catchError(err => this.handleError(err))
    );
  }

  getInterests(): Observable<Interest> {
    return this.http.get<Interest>(environment.apiUrl + 'interests').pipe(
      catchError(err => this.handleError(err))
    );
  }

  getCategories(): Observable<Category> {
    return this.http.get<Category>(environment.apiUrl + 'categories').pipe(
      catchError(err => this.handleError(err))
    );
  }

  getTypes(): Observable<Ctype> {
    return this.http.get<Ctype>(environment.apiUrl + 'types').pipe(
      catchError(err => this.handleError(err))
    );
  }

  getCoupon(id: number): Observable<Coupon> {
    return this.http.get<Coupon>(environment.apiUrl + `coupons/${id}`).pipe(
      catchError(err => this.handleError(err))
    );
  }

  editCampaign(id: number, data: object): Observable<Campaign> {
    return this.http.patch<Campaign>(environment.apiUrl + `campaigns/${id}`, data).pipe(
      catchError(err => this.handleError(err))
    );
  }

  createCoupon(data: object): Observable<Coupon> {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (isArray(data[key])) {
        data[key].forEach(el => {
          formData.append(key, el);
        });
      } else {
        formData.append(key, data[key]);
      }
    });
    return this.http.post<Coupon>(environment.apiUrl + 'coupons', formData).pipe(
      catchError(err => this.handleError(err))
    );
  }

  editCoupon(id: number, data: object): Observable<Coupon> {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (isArray(data[key])) {
        data[key].forEach(el => {
          formData.append(key, el);
        });
      } else {
        formData.append(key, data[key]);
      }
    });
    if (data['image'] === undefined) {
      formData.delete('image');
    }
    return this.http.patch<Coupon>(environment.apiUrl + `coupons/${id}`, formData).pipe(
      catchError(err => this.handleError(err))
    );
  }

  getOutlet(id: number): Observable<Outlet> {
    return this.http.get<Outlet>(environment.apiUrl + `outlets/${id}`).pipe(
      catchError(err => this.handleError(err))
    );
  }

  createOutlet(data: object): Observable<Outlet> {
    return this.http.post<Outlet>(environment.apiUrl + 'outlets', data).pipe(
      catchError(err => this.handleError(err))
    );
  }

  editOutlet(id: number, data: object): Observable<Outlet> {
    return this.http.patch<Outlet>(environment.apiUrl + `outlets/${id}`, data).pipe(
      catchError(err => this.handleError(err))
    );
  }

  getRandomString(): string {
    let result = '';
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for (let i = 0; i < 10; i++) {
      result += alphabet[Math.floor(Math.random() * (alphabet.length - 1))];
    }
    return result;
  }

  private handleError(error: HttpErrorResponse) {
    if (error instanceof ErrorEvent) {
      retry(5);
    } else {
      if (error.status === 401) {
        this.authService.logout();
        this.authService.redirectUrl = this.router.url;
        this.router.navigate(['/login']);
      }
    }
    console.log(error);
    return throwError(
      'Something bad happened; please try again later.');
  }
}
