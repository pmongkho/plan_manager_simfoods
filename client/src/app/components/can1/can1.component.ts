import { Component, OnInit } from '@angular/core'
import { PlanService } from '../../services/plan.service'
import { ApiService } from '../../services/api.service'
import { CommonModule } from '@angular/common'

@Component({
	selector: 'app-can1',
	standalone: true,
	imports: [CommonModule],
	templateUrl: './can1.component.html',
	styleUrls: ['./can1.component.css'],
})
export class Can1Component implements OnInit {
	can1Plans: any[] = []
	totalBatches: number = 0
	weightSummary: any[] = []

	constructor(
		protected planService: PlanService,
		protected apiService: ApiService
	) {}

	ngOnInit(): void {
		// Retrieve plans from the PlanService if they are already set
		const storedPlans = this.planService.getPlans('can1')
		if (storedPlans.length > 0) {
			this.can1Plans = storedPlans
			this.totalBatches = this.planService.getTotalBatches('can1')
			this.weightSummary = this.planService.getWeightSummary('can1')
		} else {
			// Fetch plans for Can1 from the API if they are not already in the service
			this.apiService.getPlansByLine('can1').subscribe(
				(data) => {
					this.can1Plans = data
					this.planService.setPlans('can1', this.can1Plans) // Store the plans in the service
				},
				(error) => {
					console.error('Error fetching Can1 plans', error)
				}
			)
		}
	}

	selectPlan(planId: string): void {
		this.planService.selectPlan('can1', planId)
		this.totalBatches = this.planService.getTotalBatches('can1')
		this.weightSummary = this.planService.getWeightSummary('can1')
	}
}
