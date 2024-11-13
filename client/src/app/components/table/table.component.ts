import {CommonModule} from '@angular/common';
import { Component, Input } from '@angular/core'
import {Weight} from '../../models/plan.model';

@Component({
	selector: 'app-table',
	standalone: true,
	imports: [CommonModule],
	templateUrl: './table.component.html',
	styleUrls: ['./table.component.css'],
})
export class TableComponent {
	@Input() tableData: Weight[] = []
	@Input() showPrint: boolean = false
	@Input() showCopy: boolean = false

	sortColumn: string = ''
	sortDirection: 'asc' | 'desc' = 'asc'

	sortTable(column: string): void {
		if (this.sortColumn === column) {
			this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
		} else {
			this.sortColumn = column
			this.sortDirection = 'asc'
		}

		this.tableData.sort((a, b) => {
		const aValue = a[column as keyof typeof a] ?? ''
		const bValue = b[column as keyof typeof b] ?? ''

			if (aValue < bValue) {
				return this.sortDirection === 'asc' ? -1 : 1
			}
			if (aValue > bValue) {
				return this.sortDirection === 'asc' ? 1 : -1
			}
			return 0
		})
	}

	// Print table content
	printTable(): void {
		const printContents = document.querySelector('.table-container')?.innerHTML
		if (printContents) {
			const printWindow = window.open('', '_blank')
			printWindow?.document.write(`
        <html>
          <head>
            <title>Print Table</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 20px; }
              table { width: 100%; border-collapse: collapse; }
              th, td { padding: 10px; border: 1px solid #333; text-align: left; }
              th { background-color: #222; color: #fff; }
            </style>
          </head>
          <body>
            ${printContents}
          </body>
        </html>
      `)
			printWindow?.document.close()
			printWindow?.print()
		}
	}

	// Copy table content to clipboard in a format suitable for pasting in Excel
	copyTable(): void {
		let tableData = 'Component\tTotal Quantity\n'
		this.tableData.forEach((item) => {
			tableData += `${item.component}\t${item.quantity}\n`
		})

		navigator.clipboard
			.writeText(tableData)
			.then(() => alert('Table copied to clipboard!'))
			.catch((err) => console.error('Failed to copy table: ', err))
	}
}
