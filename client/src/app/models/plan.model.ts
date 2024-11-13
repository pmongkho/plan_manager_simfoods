// Define the structure for a Page
export interface Page {
	id?: number // Optional for new pages (not created yet)
	front_page: string
	back_page: string
}

// Define the structure for a Weight
export interface Weight {
	id?: number // Optional for new weights (not created yet)
	component: string
	quantity: number
}

// Define the structure for a Plan
export interface Plan {
	plan_id: string
	batches: number
	progress: string
	order: number
	line: string
	pages: Page[]
	weights: Weight[]
}
