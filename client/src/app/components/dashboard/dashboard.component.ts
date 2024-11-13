import { Component, OnInit } from '@angular/core';
import {LineType, PlanService} from '../../services/plan.service';
import {Plan, Weight} from '../../models/plan.model';
import {TableComponent} from '../table/table.component';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';

@Component({
	selector: 'app-dashboard',
	standalone: true,
	imports: [TableComponent, CommonModule, FormsModule,TableComponent],
	templateUrl: './dashboard.component.html',
	styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
	nextPlans: (Weight & { line: LineType })[] = []
	nextPlansTotals: Weight[] = []
	selectedTab: 'nextPlans' | 'nextPlansTotals' = 'nextPlans'

	showCan1 = true
	showHydro = true
	showLine3 = true

	constructor(private planService: PlanService) {}

	ngOnInit(): void {
		const { nextPlans } = this.planService.getPlansByBatchWithLine(30, 40)
		this.nextPlans = nextPlans
		this.nextPlansTotals = this.calculateAggregatedTotals(nextPlans)
	}

	filterPlansByLine(
		plans: (Weight & { line: LineType })[]
	): (Weight & { line: LineType })[] {
		return plans.filter(
			(plan) =>
				(this.showCan1 && plan.line === 'can1') ||
				(this.showHydro && plan.line === 'hydro') ||
				(this.showLine3 && plan.line === 'line3')
		)
	}

	calculateAggregatedTotals(
		plans: (Weight & { line: LineType })[]
	): { component: string; quantity: number }[] {
		const totalWeights: { [key: string]: number } = {}

		// Calculate total quantity for each component across all lines
		plans.forEach((plan) => {
			totalWeights[plan.component] =
				(totalWeights[plan.component] || 0) + plan.quantity
		})

		// Convert to array format
		return Object.keys(totalWeights).map((component) => ({
			component,
			quantity: totalWeights[component],
		}))
	}
}