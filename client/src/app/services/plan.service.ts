import { Injectable } from '@angular/core'
import { BehaviorSubject } from 'rxjs'

// Define a type for the allowed lines
type LineType = 'can1' | 'hydro' | 'line3'

@Injectable({
	providedIn: 'root',
})
export class PlanService {
	private startPlanIds: { [key in LineType]: string | null } = {
		can1: null,
		hydro: null,
		line3: null,
	}

	private endPlanIds: { [key in LineType]: string | null } = {
		can1: null,
		hydro: null,
		line3: null,
	}

	private plans: { [key in LineType]: any[] } = {
		can1: [],
		hydro: [],
		line3: [],
	}

	// Store weight summary and total batches for each line
	private weightSummaries: { [key in LineType]: any[] } = {
		can1: [],
		hydro: [],
		line3: [],
	}

	private totalBatches: { [key in LineType]: number } = {
		can1: 0,
		hydro: 0,
		line3: 0,
	}

	public startPlanId$ = new BehaviorSubject<string | null>(null)
	public endPlanId$ = new BehaviorSubject<string | null>(null)

	// Set the list of plans for a specific line
	setPlans(line: LineType, plans: any[]): void {
		this.plans[line] = plans
	}

	// Get the list of plans for a specific line
	getPlans(line: LineType): any[] {
		return this.plans[line]
	}

	// Get the start plan ID for a specific line
	getStartPlanId(line: LineType): string | null {
		return this.startPlanIds[line]
	}

	// Get the end plan ID for a specific line
	getEndPlanId(line: LineType): string | null {
		return this.endPlanIds[line]
	}

	// Select a plan and update the start or end plan ID for a specific line
	selectPlan(line: LineType, planId: string): void {
		if (!this.startPlanIds[line]) {
			this.startPlanIds[line] = planId
			this.startPlanId$.next(this.startPlanIds[line])
		} else if (!this.endPlanIds[line]) {
			this.endPlanIds[line] = planId
			this.endPlanId$.next(this.endPlanIds[line])
			// Recalculate totals when both start and end plans are selected
			this.totalBatches[line] = this.calculateTotalBatches(line)
			this.weightSummaries[line] = this.calculateWeightSummary(line)
		} else {
			this.startPlanIds[line] = planId
			this.endPlanIds[line] = null
			this.startPlanId$.next(this.startPlanIds[line])
			this.endPlanId$.next(this.endPlanIds[line])
		}
	}
	// Get the total batches for the selected plans in a specific line
	getTotalBatches(line: LineType): number {
		return this.totalBatches[line]
	}

	// Get the weight summary for the selected plans in a specific line
	getWeightSummary(line: LineType): any[] {
		return this.weightSummaries[line]
	}
	calculateTotalBatches(line: LineType): number {
		const startPlanOrder =
			this.getPlanOrderById(this.startPlanIds[line], line) ?? 0
		const endPlanOrder =
			this.getPlanOrderById(this.endPlanIds[line], line) ??
			Number.MAX_SAFE_INTEGER

		return this.plans[line]
			.filter(
				(plan) => plan.order >= startPlanOrder && plan.order <= endPlanOrder
			)
			.reduce((total, plan) => total + plan.batches, 0)
	}

	calculateWeightSummary(line: LineType): any[] {
		const startPlanOrder = this.getPlanOrderById(this.startPlanIds[line], line)
		const endPlanOrder = this.getPlanOrderById(this.endPlanIds[line], line)

		if (startPlanOrder === null || endPlanOrder === null) {
			return []
		}

		const selectedPlans = this.plans[line].filter(
			(plan) => plan.order >= startPlanOrder && plan.order <= endPlanOrder
		)

		const weightSummary: { [key: string]: number } = {}

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

		return Object.keys(weightSummary).map((component) => ({
			component,
			total_quantity: weightSummary[component],
		}))
	}

	// Check if a plan is within the selected range for a specific line
	isPlanInRange(planOrder: number, line: LineType): boolean {
		const startPlanOrder = this.getPlanOrderById(this.startPlanIds[line], line)
		const endPlanOrder = this.getPlanOrderById(this.endPlanIds[line], line)

		return (
			startPlanOrder !== null &&
			endPlanOrder !== null &&
			planOrder >= startPlanOrder &&
			planOrder <= endPlanOrder
		)
	}

	// Helper to get the plan order by plan ID for a specific line
	private getPlanOrderById(
		planId: string | null,
		line: LineType
	): number | null {
		const plans = this.plans[line]
		const foundPlan = plans.find((plan) => plan.plan_id === planId)
		return foundPlan ? foundPlan.order : null
	}
}
