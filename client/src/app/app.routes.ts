import { Routes } from '@angular/router'
import {HydroComponent} from './components/hydro/hydro.component'
import {Line3Component} from './components/line3/line3.component'
import {TotalsComponent} from './components/totals/totals.component'
import {Can1Component} from './components/can1/can1.component'



export const routes: Routes = [
	{ path: 'can1', component: Can1Component },
	{ path: 'hydro', component: HydroComponent },
	{ path: 'line3', component: Line3Component },
	{ path: 'totals', component: TotalsComponent },
	{ path: '', redirectTo: '/can1', pathMatch: 'full' }, // Redirect to Can1 by default
]
