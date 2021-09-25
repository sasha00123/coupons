import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ListOutletsComponent} from './list-outlets.component';

describe('ListOutletsComponent', () => {
  let component: ListOutletsComponent;
  let fixture: ComponentFixture<ListOutletsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ListOutletsComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ListOutletsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
