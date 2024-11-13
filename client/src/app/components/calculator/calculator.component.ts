import { Component, OnInit } from '@angular/core'
import { PlanService } from '../../services/plan.service'
import { CommonModule } from '@angular/common'
import { FormsModule } from '@angular/forms'
import { TableComponent } from '../table/table.component'
import { ApiService } from '../../services/api.service'
import {Weight} from '../../models/plan.model'

@Component({
	selector: 'app-calculator',
	standalone: true,
	imports: [CommonModule, FormsModule, TableComponent],
	templateUrl: './calculator.component.html',
	styleUrls: ['./calculator.component.css'],
})
export class CalculatorComponent implements OnInit {
	selectedTab: 'single' | 'multiple' | 'pdf' = 'single'
	singleEntry = { component: '', quantity: 0 }
	bulkData: string = ''
	selectedFile: File | null = null

	// Deep copy of weights data for local modification
	calculatorWeights: Weight[] = []

	constructor(
		private planService: PlanService,
		private apiService: ApiService
	) {}

	ngOnInit(): void {}

	onFileSelected(event: Event): void {
		const input = event.target as HTMLInputElement
		if (input.files && input.files.length > 0) {
			this.selectedFile = input.files[0]
			console.log('File selected:', this.selectedFile)
			this.getPDFWeights()
		}
	}

	getPDFWeights(): void {
		if (!this.selectedFile) {
			console.warn('No file selected')
			return
		}

		this.apiService.getWeightsByPDF(this.selectedFile).subscribe((data) => {
			// Populate `bulkData` for preview only, no automatic update to `calculatorWeights`
			const extractedWeights: Weight[] = Object.keys(data).map((component) => ({
				component,
				quantity: data[component],
			}))

			// Format data for the bulkData textarea (e.g., "Component\tQuantity")
			this.bulkData = extractedWeights
				.map(
					({ component, quantity }) => `${component}\t${quantity}`
				)
				.join('\n')

			console.log('Extracted weights and populated bulkData:', this.bulkData)
		})
	}

	importTotals(): void {
		const importedWeights = this.planService.getAllWeights()

		importedWeights.forEach((importedWeight) => {
			const existingWeight = this.calculatorWeights.find(
				(w) => w.component === importedWeight.component
			)
			if (existingWeight) {
				// Add to the existing component quantity
				existingWeight.quantity += importedWeight.quantity
			} else {
				// Add as a new component if it doesn't exist
				this.calculatorWeights.push({
					component: importedWeight.component,
					quantity: importedWeight.quantity,
				})
			}
		})
	}

	subtractTotals(): void {
		const importedWeights = this.planService.getAllWeights()

		importedWeights.forEach((importedWeight) => {
			const existingWeight = this.calculatorWeights.find(
				(w) => w.component === importedWeight.component
			)
			if (existingWeight) {
				// Subtract the quantity
				existingWeight.quantity -= importedWeight.quantity
			} else {
				// If component doesn't exist, add it with a negative quantity
				this.calculatorWeights.push({
					component: importedWeight.component,
					quantity: -importedWeight.quantity,
				})
			}
		})
	}

	resetCalculatorWeights(): void {
		this.calculatorWeights = []
	}

	onSingleSubmit(action: 'add' | 'subtract'): void {
		this.updateWeights(
			this.singleEntry.component,
			this.singleEntry.quantity,
			action
		)
		this.resetSingleEntry()
	}

	onBulkSubmit(action: 'add' | 'subtract'): void {
		const entries = this.bulkData
			.split('\n')
			.map((line) => line.split('\t'))
			.filter((parts) => parts.length === 2)
			.map(([component, quantity]) => ({
				component: component.trim(),
				quantity: parseFloat(quantity.trim()),
			}))

		entries.forEach((entry) =>
			this.updateWeights(entry.component, entry.quantity, action)
		)
		this.resetBulkEntry()
	}

	updateWeights(
		component: string,
		quantity: number,
		action: 'add' | 'subtract'
	): void {
		const weight = this.calculatorWeights.find((w) => w.component === component)
		if (weight) {
			weight.quantity += action === 'add' ? quantity : -quantity
		} else {
			this.calculatorWeights.push({
				component,
				quantity: action === 'add' ? quantity : -quantity,
			})
		}
	}

	resetSingleEntry(): void {
		this.singleEntry = { component: '', quantity: 0 }
	}

	resetBulkEntry(): void {
		this.bulkData = ''
	}
}
