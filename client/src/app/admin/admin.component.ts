import { Component } from '@angular/core';
import {ApiService} from '../services/api.service';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';

@Component({
	selector: 'app-admin',
	standalone: true,
	imports: [CommonModule, FormsModule],
	templateUrl: './admin.component.html',
	styleUrl: './admin.component.css',
})
export class AdminComponent {
	selectedWeightsFile: File | null = null
	selectedBatchesFile: File | null = null
	can1: string = ''
	hydro: string = ''
	line3: string = ''

	constructor(private apiService: ApiService) {}

	onFileSelected(event: Event, fileType: 'weights' | 'batches') {
		const input = event.target as HTMLInputElement
		if (input.files && input.files.length > 0) {
			if (fileType === 'weights') {
				this.selectedWeightsFile = input.files[0]
			} else {
				this.selectedBatchesFile = input.files[0]
			}
		}
	}

	onUpload() {
		if (!this.selectedWeightsFile || !this.selectedBatchesFile) {
			alert('Please select both weights and batches files.')
			return
		}

		// Convert `can1`, `hydro`, and `line3` to use newline-separated format
		const can1Data = this.can1.replace(/\n/g, '\r\n')
		const hydroData = this.hydro.replace(/\n/g, '\r\n')
		const line3Data = this.line3.replace(/\n/g, '\r\n')

		// Prepare the form data
		const formData = new FormData()
		formData.append('weights_file', this.selectedWeightsFile)
		formData.append('batches_file', this.selectedBatchesFile)
		formData.append('can1', can1Data)
		formData.append('hydro', hydroData)
		formData.append('line3', line3Data)

		this.apiService.uploadPdfData(formData).subscribe({
			next: (response) => alert(response.message),
			error: (error) => console.error(error),
		})
	}

	onClearDatabase() {
		// Add a confirmation dialog
		const confirmClear = confirm(
			'Are you sure you want to clear the entire database? This action cannot be undone.'
		)
		if (confirmClear) {
			this.apiService.clearDatabase().subscribe({
				next: () => alert('Database cleared successfully'),
				error: (error) => console.error(error),
			})
		}
	}
}