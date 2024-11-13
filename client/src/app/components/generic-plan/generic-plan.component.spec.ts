import { ComponentFixture, TestBed } from '@angular/core/testing'

import { GenericPlanComponent } from './generic-plan.component'

describe('LineComponentComponent', () => {
	let component: GenericPlanComponent
	let fixture: ComponentFixture<GenericPlanComponent>

	beforeEach(async () => {
		await TestBed.configureTestingModule({
			imports: [GenericPlanComponent],
		}).compileComponents()

		fixture = TestBed.createComponent(GenericPlanComponent)
		component = fixture.componentInstance
		fixture.detectChanges()
	})

	it('should create', () => {
		expect(component).toBeTruthy()
	})
})
