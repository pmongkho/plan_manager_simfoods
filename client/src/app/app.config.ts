import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core'
import { RouterModule, provideRouter } from '@angular/router'
import { provideHttpClient } from '@angular/common/http'
import { importProvidersFrom } from '@angular/core' // This allows importing CommonModule, FormsModule
import { CommonModule } from '@angular/common' // Needed for ngClass
import { FormsModule } from '@angular/forms' // Needed for ngModel if you're using two-way binding
import {routes} from './app.routes'

export const appConfig: ApplicationConfig = {
	providers: [
		provideZoneChangeDetection({ eventCoalescing: true }),
		provideRouter(routes),
		provideHttpClient(),
		importProvidersFrom(CommonModule, FormsModule,RouterModule), // Add CommonModule for ngClass and FormsModule for ngModel
	],
}
