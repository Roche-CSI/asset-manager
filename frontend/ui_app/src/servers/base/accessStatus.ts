/**
 * Helper class for form related operations
 */

export const AccessStatus = {
	PUBLIC: {value: 1, label: "Public"},
	PRIVATE: {value: 2, label: "Private"},
	DELETED: {value: 3, label: "Deleted"},
	DEPRECATED: {value: 4, label: "Deprecated"},
	OBSOLETE: {value: 5, label: "Obsolete"},
	
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
