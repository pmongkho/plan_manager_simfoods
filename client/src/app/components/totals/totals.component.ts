import { ChangeDetectorRef, Component, OnInit } from '@angular/core'
import { LineType, PlanService } from '../../services/plan.service'
import { CommonModule } from '@angular/common'
import {CalculatorComponent} from '../calculator/calculator.component';
import {TableComponent} from '../table/table.component';
import {Weight} from '../../models/plan.model';

@Component({
	selector: 'app-totals',
	standalone: true,
	imports: [CommonModule, CalculatorComponent,TableComponent],
	templateUrl: './totals.component.html',
	styleUrls: ['./totals.component.css'],
})
export class TotalsComponent implements OnInit {
	totalWeights: Weight[] = []
	sortColumn: string | null = null
	sortDirection: 'asc' | 'desc' = 'asc'

	constructor(
		private planService: PlanService,
		private cdr: ChangeDetectorRef
	) {}

	ngOnInit(): void {
		this.totalWeights = this.planService.getAllWeights(this.planService.selectedPlans)
		this.cdr.detectChanges()
	}

}
