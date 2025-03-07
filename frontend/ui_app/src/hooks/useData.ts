import { useState, useEffect } from 'react';

export interface UseDataReturnType<T> {
	data: T | undefined;
	loading: boolean;
	error: string | null;
}

export const useData = <T>(fetchPromise: Promise<T>): UseDataReturnType<T> => {
	const [data, setData] = useState<T | undefined>(undefined);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);
	
	useEffect(() => {
		let isMounted = true;
		
		// Define an async function inside useEffect
		const fetchData = async () => {
			console.log("fetching data");
			setLoading(true);
			setError(null);
			
			try {
				const result = await fetchPromise;
				if (isMounted) {
					setData(result);
					setLoading(false);
				}
			} catch (err) {
				if (isMounted) {
					setError(`An error occurred while fetching data. ${err instanceof Error ? err.message : 'Unknown error'}`);
					setLoading(false);
				}
			}
		};
		
		fetchData();
		
		// Cleanup function to avoid setting state on an unmounted component
		return () => {
			isMounted = false;
		};
	}, [fetchPromise]);
	
	return { data, loading, error };
};
