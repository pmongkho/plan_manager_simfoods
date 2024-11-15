import { Injectable } from '@angular/core'
import { HttpClient } from '@angular/common/http'
import { Observable } from 'rxjs'
import {environment} from '../../environments/environments.prod'

@Injectable({
	providedIn: 'root',
})
export class ApiService {
	private apiUrl = environment.apiUrl

	constructor(private http: HttpClient) {}

	// Fetch the list of plans by line type
	getAllPlans(): Observable<any[]> {
		return this.http.get<any[]>(`${this.apiUrl}plans/`)
	}
	// Fetch the list of plans by line type
	getPlansByLine(line: string): Observable<any[]> {
		return this.http.get<any[]>(`${this.apiUrl}plans/${line}/`)
	}

	getWeightsByPDF(pdfFile: File): Observable<any> {
		const formData = new FormData()
		formData.append('pdf_file', pdfFile)
		return this.http.post(`${this.apiUrl}upload_weights_pdf/`, formData)
	}

	// Method to create a new plan
	createPlan(newPlanData: any): Observable<any> {
		return this.http.post<any>(`${this.apiUrl}plans/`, newPlanData)
	}

	// Fetch details of a specific plan by ID
	getPlanById(planId: string): Observable<any> {
		return this.http.get<any>(`${this.apiUrl}plans/${planId}/`)
	}

	// Edit a plan
	editPlan(planId: string, updatedPlanData: any): Observable<any> {
		return this.http.put<any>(`${this.apiUrl}plans/${planId}/`, updatedPlanData)
	}

	// Update order of plans
	updatePlanOrder(
		plans: { plan_id: string; order: number }[]
	): Observable<any> {
		return this.http.put<any>(`${this.apiUrl}plans/update-order/`, { plans })
	}

	// Delete a plan
	deletePlan(planId: string): Observable<any> {
		return this.http.delete<any>(`${this.apiUrl}plans/${planId}/`)
	}

	uploadPdfData(data: FormData): Observable<any> {
		return this.http.post(`${this.apiUrl}admin/upload-db/`, data)
	}

	clearDatabase(): Observable<any> {
		return this.http.delete(`${this.apiUrl}admin/clear-database/`)
	}

}
