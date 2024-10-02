import { Component, OnInit } from '@angular/core'
import { ApiService } from './services/api.service'
import { FormsModule } from '@angular/forms' // Import FormsModule
import { CommonModule } from '@angular/common' // Import CommonModule for directives like ngIf
import {RouterModule} from '@angular/router'

@Component({
	selector: 'app-root',
	standalone: true,
	imports: [FormsModule, CommonModule, RouterModule], // Import FormsModule and CommonModule
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
	// Lists of plans for each line
	can1Plans: any[] = []
	hydroPlans: any[] = []
	line3Plans: any[] = []

	// Pull lists (summary results) for each line
	can1PullList: any[] = []
	hydroPullList: any[] = []
	line3PullList: any[] = []

	// Start and end plan IDs for each line
	startCan1PlanId: string | null = null
	endCan1PlanId: string | null = null

	startHydroPlanId: string | null = null
	endHydroPlanId: string | null = null

	startLine3PlanId: string | null = null
	endLine3PlanId: string | null = null

	totalBatches: number = 0 // Variable to store total batches

	constructor(private apiService: ApiService) {}

	ngOnInit(): void {
		// Fetch plans for Can1 and sort them by order
		this.apiService.getPlansByLine('can1').subscribe(
			(data) => {
				this.can1Plans = data.sort((a, b) => a.order - b.order) // Sort by order
			},
			(error) => {
				console.error('Error fetching can1 plans', error)
			}
		)

		// Fetch plans for Hydro and sort them by order
		this.apiService.getPlansByLine('hydro').subscribe(
			(data) => {
				this.hydroPlans = data.sort((a, b) => a.order - b.order) // Sort by order
			},
			(error) => {
				console.error('Error fetching hydro plans', error)
			}
		)

		// Fetch plans for Line3 and sort them by order
		this.apiService.getPlansByLine('line3').subscribe(
			(data) => {
				this.line3Plans = data.sort((a, b) => a.order - b.order) // Sort by order
			},
			(error) => {
				console.error('Error fetching line3 plans', error)
			}
		)
	}

	selectPlan(line: string, planId: string): void {
		if (line === 'can1') {
			// If no start plan is selected, set the clicked plan as the start plan
			if (!this.startCan1PlanId) {
				this.startCan1PlanId = planId
			} else if (this.startCan1PlanId && !this.endCan1PlanId) {
				// If start plan is selected but end plan is not, set the clicked plan as the end plan
				if (planId !== this.startCan1PlanId) {
					this.endCan1PlanId = planId
				} else {
					// If the user clicks the start plan again, reset the selection
					this.startCan1PlanId = planId
					this.endCan1PlanId = null
				}
			} else {
				// If both start and end plans are already selected, start a new selection
				this.startCan1PlanId = null
				this.endCan1PlanId = null
			}

			// Calculate summary and total batches after selecting a plan
			this.autoGetSummary('can1')
			this.totalBatches = this.calculateTotalBatches('can1') // Update total batches
		} else if (line === 'hydro') {
			if (!this.startHydroPlanId) {
				this.startHydroPlanId = planId
			} else if (this.startHydroPlanId && !this.endHydroPlanId) {
				if (planId !== this.startHydroPlanId) {
					this.endHydroPlanId = planId
				} else {
					this.startHydroPlanId = planId
					this.endHydroPlanId = null
				}
			} else {
				this.startHydroPlanId = null
				this.endHydroPlanId = null
			}

			this.autoGetSummary('hydro')
			this.totalBatches = this.calculateTotalBatches('hydro')
		} else if (line === 'line3') {
			if (!this.startLine3PlanId) {
				this.startLine3PlanId = planId
			} else if (this.startLine3PlanId && !this.endLine3PlanId) {
				if (planId !== this.startLine3PlanId) {
					this.endLine3PlanId = planId
				} else {
					this.startLine3PlanId = planId
					this.endLine3PlanId = null
				}
			} else {
				this.startLine3PlanId = null
				this.endLine3PlanId = null
			}

			this.autoGetSummary('line3')
			this.totalBatches = this.calculateTotalBatches('line3')
		}
	}

	// Automatically fetch the summary when start and end plans are selected
	autoGetSummary(line: string): void {
		let startPlanId: string | null = null
		let endPlanId: string | null = null

		if (line === 'can1') {
			startPlanId = this.startCan1PlanId
			endPlanId = this.endCan1PlanId
		} else if (line === 'hydro') {
			startPlanId = this.startHydroPlanId
			endPlanId = this.endHydroPlanId
		} else if (line === 'line3') {
			startPlanId = this.startLine3PlanId
			endPlanId = this.endLine3PlanId
		}

		if (startPlanId && endPlanId) {
			this.apiService.getSummary(line, startPlanId, endPlanId).subscribe(
				(summary) => {
					// Store the summary in the appropriate variable
					if (line === 'can1') {
						this.can1PullList = summary
					} else if (line === 'hydro') {
						this.hydroPullList = summary
					} else if (line === 'line3') {
						this.line3PullList = summary
					}
				},
				(error) => {
					console.error(`Error fetching summary for ${line}`, error)
				}
			)
		}
	}

	// This function checks if a plan is within the range of start and end plans
	isPlanInRange(planOrder: number, line: string): boolean {
		let startPlanOrder: number | null = null
		let endPlanOrder: number | null = null

		// Set the start and end orders based on the line
		if (line === 'can1') {
			startPlanOrder = this.startCan1PlanId
				? this.getPlanOrderById(this.startCan1PlanId, 'can1')
				: null
			endPlanOrder = this.endCan1PlanId
				? this.getPlanOrderById(this.endCan1PlanId, 'can1')
				: null
		} else if (line === 'hydro') {
			startPlanOrder = this.startHydroPlanId
				? this.getPlanOrderById(this.startHydroPlanId, 'hydro')
				: null
			endPlanOrder = this.endHydroPlanId
				? this.getPlanOrderById(this.endHydroPlanId, 'hydro')
				: null
		} else if (line === 'line3') {
			startPlanOrder = this.startLine3PlanId
				? this.getPlanOrderById(this.startLine3PlanId, 'line3')
				: null
			endPlanOrder = this.endLine3PlanId
				? this.getPlanOrderById(this.endLine3PlanId, 'line3')
				: null
		}

		// Check if planOrder is within the start and end orders
		if (startPlanOrder !== null && endPlanOrder !== null) {
			return planOrder >= startPlanOrder && planOrder <= endPlanOrder
		}

		return false
	}
	getPlanOrderById(planId: string, line: string): number | null {
		let plans = []

		if (line === 'can1') {
			plans = this.can1Plans
		} else if (line === 'hydro') {
			plans = this.hydroPlans
		} else if (line === 'line3') {
			plans = this.line3Plans
		}

		const foundPlan = plans.find((plan) => plan.plan_id === planId)

		return foundPlan ? foundPlan.order : null
	}

	// Calculate the total batches of the plans in the selected range
	calculateTotalBatches(line: string): number {
		let totalBatches = 0 // Reset the total batches

		if (line === 'can1') {
			totalBatches = this.can1Plans
				.filter((plan) => this.isPlanInRange(plan.order, 'can1'))
				.reduce((total, plan) => total + plan.batches, 0)
		} else if (line === 'hydro') {
			totalBatches = this.hydroPlans
				.filter((plan) => this.isPlanInRange(plan.order, 'hydro'))
				.reduce((total, plan) => total + plan.batches, 0)
		} else if (line === 'line3') {
			totalBatches = this.line3Plans
				.filter((plan) => this.isPlanInRange(plan.order, 'line3'))
				.reduce((total, plan) => total + plan.batches, 0)
		}

		return totalBatches // Return total batches for the selected range
	}
}