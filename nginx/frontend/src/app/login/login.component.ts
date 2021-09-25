import {Component, OnInit} from '@angular/core';
import {AuthService} from '../auth/auth.service';
import {CookieService} from 'ngx-cookie-service';
import {ActivatedRoute, Router} from '@angular/router';
import {retry} from 'rxjs/operators';
import {DataService} from '../data.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  errors = false;
  regData = {
    email: '',
    password: ''
  };
  loading = false;

  constructor(private auth: AuthService, private cookie: CookieService,
              private router: Router) {
  }

  ngOnInit() {
    this.auth.logout();
  }

  loginUser() {
    this.loading = true;
    this.auth.loginUser(this.regData).subscribe(
      response => {
        this.cookie.set('token', response['token']);
        this.router.navigateByUrl(this.auth.redirectUrl);
      }, error => {
        if (error instanceof ErrorEvent) {
          retry(5);
        }
        this.errors = true;
        this.loading = false;
      });
  }
}
