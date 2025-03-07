export interface ElasticsearchResponse<T> {
	total: number;
	page: number;
	page_size: number;
	results: T[];
}

export interface ElasticsearchParams {
	query: string;
	filters?: Record<string, string | number | boolean | object>;
	size?: number;
	from?: number;
	sort?: Record<string, 'asc' | 'desc'>;
	username?: string;
}

export interface ElasticsearchResultWithTiming<T> extends ElasticsearchResponse<T> {
	responseTimeMs: number; // Time taken to fetch the response in milliseconds
}

export class ElasticSearch<T> {
	private apiEndpoint: string;
	private searchParams: ElasticsearchParams | null;
	
	constructor(apiEndpoint: string, initialParams: ElasticsearchParams | null = null) {
		this.apiEndpoint = apiEndpoint;
		this.searchParams = initialParams;
	}
	
	public static emptyResponse: ElasticsearchResultWithTiming<any> = {
		total: 0,
		page: 0,
		page_size: 0,
		results: [],
		responseTimeMs: 0
	};
	
	async search(params: Partial<ElasticsearchParams>): Promise<ElasticsearchResultWithTiming<T>> {
		this.searchParams = this.searchParams ? { ...this.searchParams, ...params } : params as ElasticsearchParams;
		
		if (!this.searchParams || Object.keys(this.searchParams).length === 0) {
			return ElasticSearch.emptyResponse;
		}
		
		const queryParams = new URLSearchParams();
		
		// Add query parameter if it exists
		if (this.searchParams.query) {
			queryParams.append('query', this.searchParams.query);
		}
		
		// Add size if it exists
		if (this.searchParams.size !== undefined) {
			queryParams.append('size', this.searchParams.size.toString());
		}
		
		// Add from if it exists
		if (this.searchParams.from !== undefined) {
			queryParams.append('from', this.searchParams.from.toString());
		}
		
		// Add sort if it exists
		if (this.searchParams.sort && Object.keys(this.searchParams.sort).length > 0) {
			queryParams.append('sort', JSON.stringify(this.searchParams.sort));
		}
		
		// Add filters if they exist
		if (this.searchParams.filters && Object.keys(this.searchParams.filters).length > 0) {
			queryParams.append('filters', JSON.stringify(this.searchParams.filters));
		}
		
		if (this.searchParams.username) {
			queryParams.append('user', this.searchParams.username);
		}
		
		const startTime = performance.now();
		const response = await fetch(`${this.apiEndpoint}?${queryParams.toString()}`, {credentials: 'include'});
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const result = await response.json();
		const endTime = performance.now();
		
		return {
			...result,
			responseTimeMs: endTime - startTime
		};
	}
}
