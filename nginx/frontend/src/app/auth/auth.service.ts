import {Injectable} from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {Observable} from 'rxjs';
import {CookieService} from 'ngx-cookie-service';
import {retry} from 'rxjs/operators';
import {Router} from '@angular/router';
import {DataService} from '../data.service';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  redirectUrl = '';

  constructor(private http: HttpClient, private cookie: CookieService,
              private router: Router) {
  }

  getToken(): string {
    return this.cookie.check('token') ? this.cookie.get('token') : '';
  }

  checkLogin(): boolean {
    return this.cookie.check('token');
  }

  loginUser(user: object): Observable<object> {
    return this.http.post<object>(environment.apiUrl + 'accounts/token/get', user);
  }

  registerUser(user: object): Observable<object> {
    return this.http.post<object>(environment.apiUrl + 'accounts/create', user);
  }

  logout() {
    this.cookie.delete('token');
  }
}
