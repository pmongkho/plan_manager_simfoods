import { Component, Input, OnInit } from '@angular/core'
import {
	CdkDragDrop,
	DragDropModule,
	moveItemInArray,
} from '@angular/cdk/drag-drop'
import { PlanService, LineType } from '../../services/plan.service'
import { ApiService } from '../../services/api.service'
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms'
import { Plan } from '../../models/plan.model'
import {TableComponent} from '../table/table.component'

@Component({
	selector: 'app-generic-plan',
	standalone: true,
	imports: [CommonModule, FormsModule, DragDropModule, TableComponent],
	templateUrl: './generic-plan.component.html',
	styleUrls: ['./generic-plan.component.css'],
})
export class GenericPlanComponent implements OnInit {
	@Input() planType: LineType = 'can1'
	plans: Plan[] = []
	totalBatches: number = 0
	weightSummary: any[] = []
	loading = true
	showModal = false
	selectedPlan: Plan | null = null

	constructor(
		protected planService: PlanService,
		private apiService: ApiService
	) {}

	ngOnInit(): void {
		this.loadPlans()
	}

	loadPlans() {
		this.loading = true
		const storedPlans = this.planService.getPlans(this.planType)

		if (storedPlans.length > 0) {
			this.plans = storedPlans
			this.updateTotals() // Ensure the totals only update after data is loaded
			this.loading = false
		} else {
			this.apiService.getPlansByLine(this.planType).subscribe(
				(data) => {
					this.planService.setPlans(this.planType, data) // Handle sorting in PlanService if needed
					this.plans = data
					this.updateTotals()
					this.loading = false
				},
				(error) => {
					console.error(`Error fetching ${this.planType} plans`, error)
					this.loading = false
				}
			)
		}
	}

	// Update total batches and weight summary only when necessary
	updateTotals(): void {
		this.totalBatches = this.planService.getTotalBatches(this.planType)
		this.weightSummary = this.planService.getWeightSummary(this.planType)
	}

	selectPlan(planId: string): void {
		this.planService.selectPlan(this.planType, planId)
		this.updateTotals()
	}

	resetSelection(): void {
		this.planService.resetStartAndEndPlan(this.planType)
		this.totalBatches = 0
		this.weightSummary = []
	}

	// Open modal to view/edit the selected plan
	viewPlan(plan: Plan): void {
		this.selectedPlan = { ...plan }
		this.showModal = true
	}

	// Close modal and reset selected plan
	closeModal(): void {
		this.showModal = false
		this.selectedPlan = null
	}

	savePlan(): void {
		if (this.selectedPlan) {
			this.selectedPlan.batches = Number(this.selectedPlan.batches)
			this.selectedPlan.order = Number(this.selectedPlan.order)

			// Map over nested pages and weights to ensure data consistency
			this.selectedPlan.pages = this.selectedPlan.pages.map((page) => ({
				...page,
				id: page.id ? Number(page.id) : undefined,
			}))

			this.selectedPlan.weights = this.selectedPlan.weights.map((weight) => ({
				...weight,
				id: weight.id ? Number(weight.id) : undefined,
				quantity: Number(weight.quantity),
			}))

			this.apiService
				.editPlan(this.selectedPlan.plan_id, this.selectedPlan)
				.subscribe(
					(response) => {
						console.log('Plan saved:', response)
						this.loadPlans() // Reload plans after saving to refresh data
						this.closeModal()
					},
					(error) => {
						console.error('Error saving plan:', error)
					}
				)
		}
	}

	deletePlan(plan: Plan | null): void {
		if (
			plan &&
			confirm(`Are you sure you want to delete plan ${plan.plan_id}?`)
		) {
			this.apiService.deletePlan(plan.plan_id).subscribe(
				() => {
					console.log(`Plan ${plan.plan_id} deleted.`)
					this.plans = this.plans.filter((p) => p.plan_id !== plan.plan_id)
					this.closeModal()
					this.loadPlans()
				},
				(error) => {
					console.error('Error deleting plan:', error)
				}
			)
		}
	}

	drop(event: CdkDragDrop<Plan[]>) {
		moveItemInArray(this.plans, event.previousIndex, event.currentIndex)

		// Update only the modified items' orders
		const movedPlan = this.plans[event.currentIndex]
		movedPlan.order = event.currentIndex + 1

		// Update API with the new order for this plan
		this.apiService.updatePlanOrder([movedPlan]).subscribe(
			(response) => {
				console.log(`Order updated for plan ${movedPlan.plan_id}`)
			},
			(error) => {
				console.error('Error updating plan order', error)
			}
		)
	}

	copyWeightsToClipboard(): void {
		const headers = 'Component\tTotal Quantity\n'
		const rows = this.weightSummary
			.map((item) => `${item.component}\t${item.total_quantity}`)
			.join('\n')

		const clipboardData = headers + rows

		navigator.clipboard
			.writeText(clipboardData)
			.then(() => {
				console.log('Weights data copied to clipboard')
			})
			.catch((err) => {
				console.error('Failed to copy weights data', err)
			})
	}


}
