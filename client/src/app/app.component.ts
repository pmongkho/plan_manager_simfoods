import { Component } from '@angular/core'
import { ApiService } from './api.service'
import {FormsModule} from '@angular/forms'
import {CommonModule} from '@angular/common'

@Component({
	selector: 'app-root',
	imports: [FormsModule, CommonModule], // Import FormsModule and CommonModule here

	templateUrl: './app.component.html',
	styleUrls: ['./app.component.css'],
})
export class AppComponent {
	can1Summary: any[] = []
	hydroSummary: any[] = []
	line3Summary: any[] = []

	can1StartPlanId: string = ''
	can1EndPlanId: string = ''

	hydroStartPlanId: string = ''
	hydroEndPlanId: string = ''

	line3StartPlanId: string = ''
	line3EndPlanId: string = ''

	constructor(private apiService: ApiService) {}

	// Fetch Can1 Summary
	getCan1Summary() {
		this.apiService
			.getCan1Summary(this.can1StartPlanId, this.can1EndPlanId)
			.subscribe(
				(data) => {
					this.can1Summary = data
				},
				(error) => {
					console.error('Error fetching Can1 summary', error)
				}
			)
	}

	// Fetch Hydro Summary
	getHydroSummary() {
		this.apiService
			.getHydroSummary(this.hydroStartPlanId, this.hydroEndPlanId)
			.subscribe(
				(data) => {
					this.hydroSummary = data
				},
				(error) => {
					console.error('Error fetching Hydro summary', error)
				}
			)
	}

	// Fetch Line3 Summary
	getLine3Summary() {
		this.apiService
			.getLine3Summary(this.line3StartPlanId, this.line3EndPlanId)
			.subscribe(
				(data) => {
					this.line3Summary = data
				},
				(error) => {
					console.error('Error fetching Line3 summary', error)
				}
			)
	}
}
