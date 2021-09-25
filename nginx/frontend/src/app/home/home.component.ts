import {Component, OnInit} from '@angular/core';
import {Vendor} from '../models/vendor';
import {DataService} from '../data.service';
import {Router} from '@angular/router';
import {AuthService} from '../auth/auth.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  vendor: Vendor;
  loading = true;
  disabled = true;

  constructor(private data: DataService, private auth: AuthService, private router: Router) {
  }

  ngOnInit() {
    this.data.getVendorData().subscribe(data => {
      this.vendor = data;
      if (data.organization !== null) {
        this.disabled = !data.organization.verified;
      }
      this.loading = false;
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

}
