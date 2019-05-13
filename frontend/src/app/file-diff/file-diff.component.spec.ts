import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FileDiffComponent } from './file-diff.component';

describe('FileDiffComponent', () => {
  let component: FileDiffComponent;
  let fixture: ComponentFixture<FileDiffComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FileDiffComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FileDiffComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
