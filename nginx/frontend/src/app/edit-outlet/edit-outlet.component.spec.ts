import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {EditOutletComponent} from './edit-outlet.component';

describe('EditOutletComponent', () => {
  let component: EditOutletComponent;
  let fixture: ComponentFixture<EditOutletComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [EditOutletComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditOutletComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
