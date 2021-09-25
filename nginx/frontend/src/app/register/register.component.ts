import {Component, OnInit} from '@angular/core';
import {AuthService} from '../auth/auth.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  errors = {
    username: false,
    email: false,
    connection: false
  };
  regData = {
    username: '',
    email: '',
    password: '',
    atype: 'V'
  };

  loading = false;

  constructor(private auth: AuthService, private router: Router) {
  }

  ngOnInit() {
    this.auth.logout();
  }

  registerUser() {
    this.loading = true;
    this.auth.registerUser(this.regData).subscribe(
      data => {
        this.router.navigate(['/login']);
      },
      err => {
        this.errors.connection = err instanceof ErrorEvent;
        this.errors.username = err.error.hasOwnProperty('username');
        this.errors.email = err.error.hasOwnProperty('email');
        this.loading = false;
      }
    );
  }

}
