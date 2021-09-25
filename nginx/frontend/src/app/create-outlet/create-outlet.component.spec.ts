import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {CreateOutletComponent} from './create-outlet.component';

describe('CreateOutletComponent', () => {
  let component: CreateOutletComponent;
  let fixture: ComponentFixture<CreateOutletComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [CreateOutletComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateOutletComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
