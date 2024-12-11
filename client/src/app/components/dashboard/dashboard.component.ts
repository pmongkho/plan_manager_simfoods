import { Component, OnInit } from '@angular/core';
import {LineType, PlanService} from '../../services/plan.service';
import {Plan, Weight} from '../../models/plan.model';
import {TableComponent} from '../table/table.component';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';

@Component({
	selector: 'app-dashboard',
	standalone: true,
	imports: [TableComponent, CommonModule, FormsModule, TableComponent],
	templateUrl: './dashboard.component.html',
	styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
	ngOnInit(): void {
		throw new Error('Method not implemented.');
	}

	
}