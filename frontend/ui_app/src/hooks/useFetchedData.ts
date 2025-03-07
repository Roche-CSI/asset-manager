import { useMemo } from 'react';
import {useData, UseDataReturnType} from "./useData";

export const useFetchedData = <T, >(fetchFunction: () => Promise<unknown>) => {
	const promise = useMemo(() => fetchFunction(), [fetchFunction]);
	return useData(promise) as UseDataReturnType<T[]>;
};
