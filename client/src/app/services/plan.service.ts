import { Injectable } from '@angular/core'
import { BehaviorSubject } from 'rxjs'
import { Plan, Weight } from '../models/plan.model'

export type LineType = 'can1' | 'hydro' | 'line3'

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

	public plans: { [key in LineType]: Plan[] } = {
		can1: [],
		hydro: [],
		line3: [],
	}

	public selectedPlans: { [key in LineType]: Plan[] } = {
		can1: [],
		hydro: [],
		line3: [],
	}

	public nextPlans: { [key in LineType]: Plan[] } = {
		can1: [],
		hydro: [],
		line3: [],
	}

	public startPlanId$ = new BehaviorSubject<string | null>(null)
	public endPlanId$ = new BehaviorSubject<string | null>(null)

	// Set and sort plans for a specific line
	setPlans(line: LineType, plans: Plan[]): void {
		this.plans[line] = plans.sort((a, b) => a.order - b.order)
	}

	// Get all plans for a specific line
	getPlans(line: LineType): Plan[] {
		return this.plans[line]
	}

	// Get the starting plan ID for a line
	getStartPlanId(line: LineType): string | null {
		return this.startPlanIds[line]
	}

	// Get the ending plan ID for a line
	getEndPlanId(line: LineType): string | null {
		return this.endPlanIds[line]
	}

	/**
	 * Select or deselect plans in a given range.
	 * If the range includes already selected plans, it will deselect them and move them back to the plans list.
	 * @param line LineType
	 * @param startOrder Starting order of range
	 * @param endOrder Ending order of range
	 */
	togglePlansInRange(
		line: LineType,
		planId: string,
		targetVariable: 'selectedPlans' | 'nextPlans'
	): void {
		const targetArray =
			targetVariable === 'selectedPlans'
				? this.selectedPlans[line]
				: this.nextPlans[line]

		const selectedPlan = this.plans[line].find((p) => p.plan_id === planId)

		if (!selectedPlan) return // Ensure the plan exists

		if (!this.startPlanIds[line]) {
			// Set start plan ID
			this.startPlanIds[line] = planId
			this.startPlanId$.next(this.startPlanIds[line])

			if (!targetArray.some((p) => p.plan_id === planId)) {
				const updatedArray = [...targetArray, selectedPlan]
				targetVariable === 'selectedPlans'
					? (this.selectedPlans[line] = updatedArray)
					: (this.nextPlans[line] = updatedArray)
			}
		} else if (!this.endPlanIds[line]) {
			// Set end plan ID and select range
			this.endPlanIds[line] = planId
			this.endPlanId$.next(this.endPlanIds[line])

			const startOrder = this.getPlanOrderById(this.startPlanIds[line], line)
			const endOrder = this.getPlanOrderById(this.endPlanIds[line], line)

			if (startOrder !== null && endOrder !== null) {
				const rangePlans = this.getPlansInRange(
					line,
					Math.min(startOrder, endOrder),
					Math.max(startOrder, endOrder)
				)

				const updatedArray = [
					...targetArray,
					...rangePlans.filter(
						(plan) => !targetArray.some((p) => p.plan_id === plan.plan_id)
					),
				]

				targetVariable === 'selectedPlans'
					? (this.selectedPlans[line] = updatedArray)
					: (this.nextPlans[line] = updatedArray)
			}
		} else {
			// Reset if both start and end are already set
			this.resetStartAndEndPlan(line, targetVariable)
		}
	}

	// Reset start and end plan IDs for a line
	resetStartAndEndPlan(
		line: LineType,
		targetVariable: 'selectedPlans' | 'nextPlans'
	): void {
		// Reset `startPlanIds` and `endPlanIds` for the line
		this.startPlanIds[line] = null
		this.endPlanIds[line] = null
		this.startPlanId$.next(this.startPlanIds[line])
		this.endPlanId$.next(this.endPlanIds[line])

		if (targetVariable === 'selectedPlans') {
			// Handle `selectedPlans`
			const selectedPlanIds = new Set(
				this.selectedPlans[line].map((p) => p.plan_id)
			)
			this.plans[line] = [
				...this.plans[line],
				...this.selectedPlans[line].filter(
					(selectedPlan) =>
						!this.plans[line].some(
							(plan) => plan.plan_id === selectedPlan.plan_id
						)
				),
			]
			this.selectedPlans[line] = []
		} else if (targetVariable === 'nextPlans') {
			// Handle `nextPlans`
			const nextPlanIds = new Set(this.nextPlans[line].map((p) => p.plan_id))
			this.plans[line] = [
				...this.plans[line],
				...this.nextPlans[line].filter(
					(nextPlan) =>
						!this.plans[line].some((plan) => plan.plan_id === nextPlan.plan_id)
				),
			]
			this.nextPlans[line] = []
		}

		// Ensure `plans` is sorted after resetting
		this.plans[line].sort((a, b) => a.order - b.order)
	}

	isPlanSelected(plan: Plan, line: LineType): boolean {
		return this.selectedPlans[line].some((p) => p.plan_id === plan.plan_id)
	}

	// Calculate total batches for selected plans
	getTotalBatches(selectedPlans: Plan[]): number {
		return selectedPlans.reduce((total, plan) => total + (plan.batches || 0), 0)
	}

	// Get plans in a specified order range
	getPlansInRange(
		line: LineType,
		startOrder: number,
		endOrder: number
	): Plan[] {
		return this.plans[line].filter(
			(plan) => plan.order >= startOrder && plan.order <= endOrder
		)
	}

	// Get the order of a plan by ID
	private getPlanOrderById(
		planId: string | null,
		line: LineType
	): number | null {
		const foundPlan = this.plans[line].find((plan) => plan.plan_id === planId)
		return foundPlan ? foundPlan.order : null
	}

	// Get the next set of plans starting from the endPlanId
	getPlansNext(line: LineType, minBatches: number, maxBatches: number): Plan[] {
		const linePlans = this.plans[line]
		const endPlanId = this.endPlanIds[line]

		let startIndex = 0
		if (endPlanId) {
			const endPlanIndex = linePlans.findIndex(
				(plan) => plan.plan_id === endPlanId
			)
			startIndex = endPlanIndex !== -1 ? endPlanIndex + 1 : 0 // Start from the next plan
		}

		let currentBatchCount = 0
		const nextPlans: Plan[] = []

		for (let i = startIndex; i < linePlans.length; i++) {
			const plan = linePlans[i]
			if (currentBatchCount + plan.batches > maxBatches) break
			nextPlans.push(plan)
			currentBatchCount += plan.batches
			if (currentBatchCount >= minBatches) break
		}

		return nextPlans
	}

	// Calculate weight summary for a given set of plans
	getWeightSummaryForLine(plans: Plan[]): Weight[] {
		const weightSummary: { [key: string]: number } = {}

		plans.forEach((plan) => {
			plan.weights.forEach((weight) => {
				weightSummary[weight.component] =
					(weightSummary[weight.component] || 0) + weight.quantity
			})
		})

		return Object.keys(weightSummary).map((component) => ({
			component,
			quantity: weightSummary[component],
		}))
	}

	// Get all weights for all lines
	// Get all weights for all lines (works for both plans and selectedPlans)
	getAllWeights(data: { [key in LineType]: Plan[] }): Weight[] {
		const totalWeights: { [key: string]: number } = {}

		// Loop through all lines and calculate weights
		const lines: LineType[] = ['can1', 'hydro', 'line3']
		lines.forEach((line) => {
			// Use getWeightSummaryForPlan with the data for the current line
			const lineWeights = this.getWeightSummaryForLine(data[line])

			lineWeights.forEach((weight) => {
				totalWeights[weight.component] =
					(totalWeights[weight.component] || 0) + weight.quantity
			})
		})

		// Convert the total weights to an array of Weight objects
		return Object.keys(totalWeights).map((component) => ({
			component,
			quantity: totalWeights[component],
		}))
	}
}
