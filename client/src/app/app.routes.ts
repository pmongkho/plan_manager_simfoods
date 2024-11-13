import { Routes } from '@angular/router'
import { TotalsComponent } from './components/totals/totals.component'
import { UploadComponent } from './components/upload/upload.component'
import { ErrorsComponent } from './components/errors/errors.component'
import {PlansComponent} from './components/plans/plans.component'
import {CalculatorComponent} from './components/calculator/calculator.component'
import {DashboardComponent} from './components/dashboard/dashboard.component'
import {AdminComponent} from './admin/admin.component'

export const routes: Routes = [
	{path: 'plans', component: PlansComponent},
	{path: 'admin', component: AdminComponent},
	{ path: 'dashboard', component: DashboardComponent }, // Redirect to totals component for now
	{path: 'totals', component: TotalsComponent},
	{ path: 'calculator', component: CalculatorComponent }, // Redirect to totals component for now
	{ path: 'upload', component: UploadComponent },
	{ path: 'errors', component: ErrorsComponent },
	{ path: '', redirectTo: '/plans', pathMatch: 'full' }, // Default route
]
