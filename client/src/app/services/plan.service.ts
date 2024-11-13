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

	private plans: { [key in LineType]: Plan[] } = {
		can1: [],
		hydro: [],
		line3: [],
	}

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

	// check to see if i really have to sort here or backend
	setPlans(line: LineType, plans: Plan[]): void {
		this.plans[line] = plans.sort((a, b) => a.order - b.order)
	}

	getPlans(line: LineType): Plan[] {
		return this.plans[line]
	}

	getStartPlanId(line: LineType): string | null {
		return this.startPlanIds[line]
	}

	getEndPlanId(line: LineType): string | null {
		return this.endPlanIds[line]
	}

	selectPlan(line: LineType, planId: string): void {
		if (!this.startPlanIds[line]) {
			this.startPlanIds[line] = planId
			this.startPlanId$.next(this.startPlanIds[line])
		} else if (!this.endPlanIds[line]) {
			this.endPlanIds[line] = planId
			this.endPlanId$.next(this.endPlanIds[line])
			this.totalBatches[line] = this.calculateTotalBatches(line)
			this.weightSummaries[line] = this.calculateWeightSummary(line)
		} else {
			this.startPlanIds[line] = planId
			this.endPlanIds[line] = null
			this.startPlanId$.next(this.startPlanIds[line])
			this.endPlanId$.next(this.endPlanIds[line])
			this.totalBatches[line] = 0
			this.weightSummaries[line] = []
		}
	}

	getTotalBatches(line: LineType): number {
		return this.totalBatches[line]
	}

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
			.reduce((total, plan) => total + (plan.batches || 0), 0)
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
					if (!weight.component.startsWith('RN')) {
						weightSummary[weight.component] =
							(weightSummary[weight.component] || 0) + weight.quantity
					}
				}
			)
		})

		return Object.keys(weightSummary).map((component) => ({
			component,
			total_quantity: weightSummary[component],
		}))
	}

	getPlansByBatchWithLine(
		minBatches: number,
		maxBatches: number
	): {
		nextPlans: (Weight & { line: LineType })[]
		remainingPlans: (Weight & { line: LineType })[]
	} {
		const result: {
			nextPlans: (Weight & { line: LineType })[]
			remainingPlans: (Weight & { line: LineType })[]
		} = { nextPlans: [], remainingPlans: [] }

		for (const line of ['can1', 'hydro', 'line3'] as LineType[]) {
			const { nextPlans, remainingPlans } = this.getPlansByBatch(
				line,
				minBatches,
				maxBatches
			)

			// Calculate weight summaries and add line information
			const nextWeightSummary = this.calculateWeightSummaryForPlans(
				nextPlans
			).map((weight) => ({
				...weight,
				line,
			}))

			const remainingWeightSummary = this.calculateWeightSummaryForPlans(
				remainingPlans
			).map((weight) => ({
				...weight,
				line,
			}))

			result.nextPlans.push(...nextWeightSummary)
			result.remainingPlans.push(...remainingWeightSummary)
		}

		return result
	}

	getAllWeights(): Weight[] {
		const totalWeights: { [key: string]: number } = {}

		const lines: LineType[] = ['can1', 'hydro', 'line3']
		lines.forEach((line) => {
			const lineWeights = this.calculateWeightSummary(line)

			lineWeights.forEach((weight) => {
				totalWeights[weight.component] =
					(totalWeights[weight.component] || 0) + weight.total_quantity
			})
		})

		return Object.keys(totalWeights).map((component) => ({
			component,
			quantity: totalWeights[component],
		}))
	}

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

	private getPlanOrderById(
		planId: string | null,
		line: LineType
	): number | null {
		const foundPlan = this.plans[line].find((plan) => plan.plan_id === planId)
		return foundPlan ? foundPlan.order : null
	}

	resetStartAndEndPlan(line: LineType): void {
		this.startPlanIds[line] = null
		this.endPlanIds[line] = null

		this.startPlanId$.next(this.startPlanIds[line])
		this.endPlanId$.next(this.endPlanIds[line])

		this.totalBatches[line] = 0
		this.weightSummaries[line] = []
	}

	getPlansByBatch(line: LineType, minBatches: number, maxBatches: number) {
		const linePlans = this.plans[line]
		let currentBatchCount = 0
		const nextPlans: Plan[] = []
		const remainingPlans: Plan[] = []

		// Collect next plans up to the required batch count
		for (const plan of linePlans) {
			if (currentBatchCount >= minBatches) break
			nextPlans.push(plan)
			currentBatchCount += plan.batches
		}

		// Collect remaining plans after the next set
		for (const plan of linePlans.slice(nextPlans.length)) {
			remainingPlans.push(plan)
		}

		return { nextPlans, remainingPlans }
	}

	calculateWeightSummaryForPlans(plans: Plan[]): Weight[] {
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
}
