/* eslint-disable no-mixed-spaces-and-tabs */
import { useState, useMemo } from 'react';
import {isArray} from "lodash";

// Define the hook's parameters and return types
interface UseSearchProps<T, F> {
	initialSearchText?: string;
	data: T[];
	filterFunction: (query: F, data: T[]) => T[];
	resetFunction?: () => void;
}

export interface FilterResults<T, F> {
	items: T[],
	handleSearch: (searchTerm: F) => void,
	resetSearch: () => void,
}


export const useFilter = <T, F>({
	                                initialSearchText = '',
	                                data,
	                                filterFunction
                                }: UseSearchProps<T, F>): FilterResults<T, F> => {
	const [searchTerm, setSearchTerm] = useState<F>(initialSearchText as unknown as F);
	
	// Memoize filtered data based on search text
	const items = useMemo(() => {
		const searchLength = isArray(searchTerm) ? searchTerm.length : (searchTerm as string).length;
		if (searchLength === 0) {
			return data;
		}
		return data && data.length > 0 ? filterFunction(searchTerm, data): [];
	}, [searchTerm, data, filterFunction]);
	
	const resetSearch = () => {
		if (isArray(searchTerm)) {
			setSearchTerm([] as unknown as F);
		}else {
			setSearchTerm('' as unknown as F);
		}
	}
	
	// Handler to update search text
	const handleSearch = (searchTerm: F) => {
		setSearchTerm(searchTerm);
	};
	
	return {items, handleSearch, resetSearch};
};
