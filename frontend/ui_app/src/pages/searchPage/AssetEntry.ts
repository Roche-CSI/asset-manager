import { TagGroup } from "./pages/searchPage/taggable";

export interface AssetEntry {
	id: string;
	title: string;
	description: string;
	tags: string[];
	metadata: Record<string, any>;
	class_name: string;
	class_id: string;
	class_title: string;
	class_type: string;
	project_name: string;
	project_title: string;
	project_id: string;
	root_version: Record<string, any>;
	leaf_version: Record<string, any>;
	owner: string;
	created_by: string;
	created_at: number;
	modified_by: string;
	modified_at: number;
	alias: string;
	seq_id: number;
	name: string;
	num_versions: number;
	status: number;
	class_status: number;
	project_status: number;
	es_score: number;
	es_highlight: Record<string, string[]>;
}

export default class AssetSearchResult {
	total: number;
	page: number;
	page_size: number;
	results: AssetEntry[];
	
	constructor({ total, page, page_size, results }: { total: number; page: number; page_size: number; results: AssetEntry[] }) {
		this.total = total;
		this.page = page;
		this.page_size = page_size;
		this.results = results;
	}
	
	/**
	 * Recursively merge metadata objects
	 * @param target - The target object to merge into
	 * @param source - The source object to merge from
	 */
	private mergeMetadata(target: Record<string, any>, source: Record<string, any>) {
		for (const key in source) {
			if (typeof source[key] === 'object' && source[key] !== null) {
				if (!target[key]) target[key] = {};
				this.mergeMetadata(target[key], source[key]);
			} else {
				if (!target[key]) target[key] = true;
			}
		}
	}
	
	/**
	 * Collect all metadata keys from the search results, preserving the nested structure
	 * @returns A nested dictionary representing the structure of all metadata keys
	 */
	collectAllMetadataKeys(): Record<string, any> {
		const metadataStructure: Record<string, any> = {};
		
		this.results.forEach(result => {
			if (result.metadata) {
				this.mergeMetadata(metadataStructure, result.metadata);
			}
		});
		
		return metadataStructure;
	}
	
	/**
	 * Extract unique tags from the search results
	 * @returns An array of unique tags
	 */
	extractUniqueTags(): string[] {
		return Array.from(new Set(this.results.map((result) => result.tags).flat()));
	}
	
	/**
	 * Extract unique highlight keys from the search results
	 * @returns An array of unique highlight keys
	 */
	extractUniqueHighlightKeys(exclude: string[]): string[] {
		const highlightKeys = new Set<string>();
		this.results.forEach(result => {
			if (result.es_highlight) {
				Object.keys(result.es_highlight).forEach(key => {
					highlightKeys.add(key);
				});
			}
		});
		// console.log("highlightKeys", highlightKeys);
		// remove excluded keys if present
		exclude.forEach(key => {
			highlightKeys.delete(key);
		});
		const result = Array.from(highlightKeys);
		// remove .ngram and .text from end of keys
		// result.forEach((key, index) => {
		// 	if (key.endsWith('.ngram')) {
		// 		result[index] = key.slice(0, -6);
		// 	} else if (key.endsWith('.text')) {
		// 		result[index] = key.slice(0, -5);
		// 	}
		// });
		return result;
		
	}
	
	/**
	 * Filter an asset based on the given tag group
	 * @param tagGroup - The tag group to filter by
	 * @param asset - The asset to filter
	 * @returns A boolean indicating whether the asset passes the filter
	 */
	filterAsset(tagGroup: TagGroup, asset: AssetEntry): boolean {
		switch (tagGroup.name) {
			case "tags":
				const selectedTags = tagGroup.categories.flatMap(category =>
					Object.keys(category.selected || {})
				);
				if (selectedTags.length === 0) return true;
				return selectedTags.some(tag => asset.tags.includes(tag));
			
			case "highlights":
				const selectedHighlights = tagGroup.categories.flatMap(category =>
					Object.keys(category.selected || {})
				);
				if (selectedHighlights.length === 0) return true;
				return selectedHighlights.some(highlight =>
					Object.keys(asset.es_highlight || {}).includes(highlight)
				);
			
			default:
				console.warn(`Unhandled tag group type: ${tagGroup.name}`);
				return false;
		}
	}
	
	/**
	 * Filter the results based on the given tag groups
	 * @param tagGroups - An array of tag groups to filter by
	 * @returns A new AssetSearchResult with filtered results
	 */
	filterResults(tagGroups: TagGroup[]): AssetSearchResult {
		const filteredResults = this.results.filter(asset =>
			tagGroups.every(tagGroup => this.filterAsset(tagGroup, asset))
		);
		
		return new AssetSearchResult({
			total: filteredResults.length,
			page: this.page,
			page_size: this.page_size,
			results: filteredResults
		});
	}
}
