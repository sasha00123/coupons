// src/app/auth/token.interceptor.ts

import {Injectable} from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import {AuthService} from './auth/auth.service';
import {Observable} from 'rxjs';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {

  constructor(public auth: AuthService) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    if (this.auth.checkLogin()) {
      request = request.clone({
        setHeaders: {
          Authorization: `JWT ${this.auth.getToken()}`
        }
      });
    }
    return next.handle(request);
  }
}
