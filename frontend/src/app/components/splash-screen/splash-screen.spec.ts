import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SplashScreen } from './splash-screen';

describe('Loader', () => {
  let component: SplashScreen;
  let fixture: ComponentFixture<SplashScreen>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SplashScreen],
    }).compileComponents();

    fixture = TestBed.createComponent(SplashScreen);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
