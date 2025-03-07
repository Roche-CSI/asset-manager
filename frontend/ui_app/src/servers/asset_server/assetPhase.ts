/**
 * Helper class for asset edit form related operations
 */

export const AssetPhase = {
	NOT_APPLICABLE: {value: 0, label: 'Not-Applicable'},
	DRAFT: {value: 1, label: "Draft"},
	EXPERIMENTAL: {value: 2, label: "Experimental"},
	BETA: {value: 3, label: "Beta"},
	RELEASED: {value: 4, label: "Released"},
	STABLE: {value: 5, label: "Stable"},
	
	// Utility method to get the field name by value
	getFieldByValue(value: number) {
		for (const [field, data] of Object.entries(this)) {
			if (typeof data === 'object' && data.value === value) {
				return field;
			}
		}
		return null;
	},
	
	// Utility method to get the label by value
	getLabelByValue(value: number) {
		for (const data of Object.values(this)) {
			if (typeof data === 'object' && data.value === value) {
				return data.label;
			}
		}
		return null;
	},
	
	getAll() {
		return Object.values(this);
	}
};
