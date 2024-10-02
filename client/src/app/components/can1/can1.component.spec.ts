import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Can1Component } from './can1.component';

describe('Can1Component', () => {
  let component: Can1Component;
  let fixture: ComponentFixture<Can1Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Can1Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Can1Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
