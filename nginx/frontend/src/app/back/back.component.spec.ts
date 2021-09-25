import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BackComponent } from './back.component';

describe('BackComponent', () => {
  let component: BackComponent;
  let fixture: ComponentFixture<BackComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BackComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BackComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
