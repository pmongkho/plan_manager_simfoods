import { Injectable } from '@angular/core'
import { BehaviorSubject } from 'rxjs'

@Injectable({
	providedIn: 'root',
})
export class PlanService {
	private startPlanId: string | null = null
	private endPlanId: string | null = null
	private plans: any[] = [] // This will hold all plans for all lines (can1, hydro, line3)

	public startPlanId$ = new BehaviorSubject<string | null>(null)
	public endPlanId$ = new BehaviorSubject<string | null>(null)

	// Set the list of plans
	setPlans(plans: any[]): void {
		this.plans = plans
	}

	// Select a plan and update the start or end plan ID
	selectPlan(planId: string): void {
		if (!this.startPlanId) {
			this.startPlanId = planId
			this.startPlanId$.next(this.startPlanId)
		} else if (!this.endPlanId) {
			this.endPlanId = planId
			this.endPlanId$.next(this.endPlanId)
		} else {
			this.startPlanId = planId
			this.endPlanId = null
			this.startPlanId$.next(this.startPlanId)
			this.endPlanId$.next(this.endPlanId)
		}
	}

	// Calculate the total batches for the selected plans
	calculateTotalBatches(): number {
		let totalBatches = 0 // Reset the total batches

		// Ensure start and end plan orders are not null
		const startPlanOrder = this.getPlanOrderById(this.startPlanId) ?? 0
		const endPlanOrder =
			this.getPlanOrderById(this.endPlanId) ?? Number.MAX_SAFE_INTEGER

		// Calculate total batches for plans in the range
		totalBatches = this.plans
			.filter(
				(plan) => plan.order >= startPlanOrder && plan.order <= endPlanOrder
			)
			.reduce((total, plan) => total + plan.batches, 0)

		return totalBatches
	}

	// Calculate the summary of weights for the selected range
	calculateWeightSummary(): any[] {
		// Ensure start and end plan IDs are available
		if (!this.startPlanId || !this.endPlanId) return []

		// Get the order values of the start and end plans
		const startPlanOrder = this.getPlanOrderById(this.startPlanId)
		const endPlanOrder = this.getPlanOrderById(this.endPlanId)

		// Check if either startPlanOrder or endPlanOrder is null
		if (startPlanOrder === null || endPlanOrder === null) {
			return []
		}

		// Filter the plans within the selected range (inclusive of start and end orders)
		const selectedPlans = this.plans.filter(
			(plan) => plan.order >= startPlanOrder && plan.order <= endPlanOrder
		)

		const weightSummary: any = {}

		// Aggregate the weights from all selected plans
		selectedPlans.forEach((plan) => {
			plan.weights.forEach(
				(weight: { component: string; quantity: number }) => {
					if (!weightSummary[weight.component]) {
						weightSummary[weight.component] = 0
					}
					weightSummary[weight.component] += weight.quantity
				}
			)
		})

		// Convert the summary object to an array format
		return Object.keys(weightSummary).map((component) => ({
			component,
			total_quantity: weightSummary[component],
		}))
	}

	// Check if a plan is within the selected range
	isPlanInRange(planOrder: number): boolean {
		const startPlanOrder = this.getPlanOrderById(this.startPlanId)
		const endPlanOrder = this.getPlanOrderById(this.endPlanId)

		// Ensure startPlanOrder and endPlanOrder are not null before comparing
		if (startPlanOrder !== null && endPlanOrder !== null) {
			return planOrder >= startPlanOrder && planOrder <= endPlanOrder
		}

		// If either startPlanOrder or endPlanOrder is null, return false
		return false
	}

	// Helper to get the plan order by plan ID
	private getPlanOrderById(planId: string | null): number | null {
		const foundPlan = this.plans.find((plan) => plan.plan_id === planId)
		return foundPlan ? foundPlan.order : null
	}
}
