// src/app/api.service.ts
import { Injectable } from '@angular/core'
import { HttpClient, HttpParams } from '@angular/common/http'
import { Observable } from 'rxjs'

@Injectable({
	providedIn: 'root',
})
export class ApiService {
	private apiUrl = 'http://localhost:8000/api/' // Adjust Django backend URL as needed

	constructor(private http: HttpClient) {}

	getCan1Summary(startPlanId: string, endPlanId: string): Observable<any> {
		const params = new HttpParams()
			.set('start_plan_id', startPlanId)
			.set('end_plan_id', endPlanId)
		return this.http.get<any>(`${this.apiUrl}can1_pulllist/`, { params })
	}

	getHydroSummary(startPlanId: string, endPlanId: string): Observable<any> {
		const params = new HttpParams()
			.set('start_plan_id', startPlanId)
			.set('end_plan_id', endPlanId)
		return this.http.get<any>(`${this.apiUrl}hydro_pulllist/`, { params })
	}

	getLine3Summary(startPlanId: string, endPlanId: string): Observable<any> {
		const params = new HttpParams()
			.set('start_plan_id', startPlanId)
			.set('end_plan_id', endPlanId)
		return this.http.get<any>(`${this.apiUrl}line3_pulllist/`, { params })
	}
}
