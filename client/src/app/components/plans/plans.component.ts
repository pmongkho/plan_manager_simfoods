import { Component } from '@angular/core'
import { GenericPlanComponent } from '../generic-plan/generic-plan.component'

@Component({
	selector: 'app-plans',
	standalone: true,
	imports: [GenericPlanComponent], // Import GenericPlanComponent here
	templateUrl: './plans.component.html',
	styleUrls: ['./plans.component.css'],
})
export class PlansComponent {}
