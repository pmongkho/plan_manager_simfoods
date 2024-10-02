import { Injectable } from '@angular/core'
import { HttpClient, HttpParams } from '@angular/common/http'
import { Observable } from 'rxjs'

@Injectable({
	providedIn: 'root',
})
export class ApiService {
	private apiUrl = 'http://localhost:8000/api/' // Adjust Django backend URL as needed

	constructor(private http: HttpClient) {}

	// Fetch the list of plans by line type
	getPlansByLine(line: string): Observable<any[]> {
		return this.http.get<any[]>(`${this.apiUrl}plans/${line}/`) // API to get plans for each line
	}

	// Fetch the summary based on the selected start and end plan IDs for a specific line
	getSummary(
		line: string,
		startPlanId: string,
		endPlanId: string
	): Observable<any> {
		const params = new HttpParams()
			.set('start_plan_id', startPlanId)
			.set('end_plan_id', endPlanId)
		return this.http.get<any>(`${this.apiUrl}pulllist/${line}/`, {
			params,
		})
	}
}
