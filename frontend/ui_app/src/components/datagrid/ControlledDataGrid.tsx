import React, {useEffect, useRef, useState} from 'react';
import { max } from "lodash";
import { Pagination } from "./Pagination";

export interface DataCardProps<T> {
	item: T;
	routeGenerator?: (resource: string, id: string) => string;
}

export interface RouteGenerator {
	(resource: string, id: string): string;
}

interface GridProps<T> {
	items: T[];
	itemCard: React.FC<DataCardProps<T>>;
	routeGenerator?: RouteGenerator;
	className?: string;
	cols?: number;
	numOfPages?: number;
	length: number;
	currentPage?: number;
	rowsPerPage?: number;
	onPageChange?: (page: number, rowsPerPage: number) => void;
	onRowsPerPageChange?: (rowsPerPage: number) => void;
	selfPagination?: boolean; // If true, the component will handle pagination, assumes that the items contain the full list
}

export const ControlledDataGrid = <T,>({
	                                       items,
	                                       itemCard: DataCard,
	                                       className,
	                                       routeGenerator,
	                                       cols = 3,
	                                       numOfPages = 10,
	                                       length = 0,
	                                       currentPage = 1,
	                                       rowsPerPage = 10,
	                                       onPageChange,
	                                       onRowsPerPageChange,
	                                       selfPagination = true
                                       }: GridProps<T>) => {
	const initializedRef = useRef(false);
	const [numRowsPerPage, setRowsPerPage] = useState<number>(rowsPerPage);
	const [focusPage, setFocusPage] = useState<number>(currentPage);
	const startIndex = selfPagination ? max([(focusPage - 1) * numRowsPerPage, 0]) || 0 : (currentPage - 1) * rowsPerPage;
	const endIndex = Math.min(startIndex + rowsPerPage - 1, length)
	
	useEffect(() => {
		if (!initializedRef.current) {
			initializedRef.current = true;
		}
	}, []);
	
	const handlePageChange = (page: number) => {
		setFocusPage(page);
		onPageChange && onPageChange(page, numRowsPerPage);
	};

	const handleRowsPerPageChange = (rowsPerPage: number) => {
		setRowsPerPage(rowsPerPage);
		onRowsPerPageChange && onRowsPerPageChange(rowsPerPage);
    	onPageChange && onPageChange(1, rowsPerPage);
	}
	
	// Dynamic class for grid columns
	const gridColsClass = `grid-cols-1 md:grid-cols-2 lg:grid-cols-${cols - 1} xl:grid-cols-${cols}`;
	return (
		<React.Fragment>
			{items.length === 0 && 
				<div className="h-32 border border-base-300 rounded-md w-full">
				<div className="flex justify-center items-center h-full text-neutral-500">
					No data available
				</div>
			</div>
			}
			<div className={`grid gap-4 ${gridColsClass} ${className || ''}`}>
				{items.map((item, index) => (
					<DataCard
						key={index}
						item={item}
						routeGenerator={routeGenerator}
					/>
				))}
			</div>
			<Pagination
				startIndex={startIndex + 1}
				endIndex={endIndex}
				totalCount={length}
				totalPages={numOfPages}
				currentPage={currentPage}
				onPageChange={handlePageChange}
				rowsPerPage={rowsPerPage}
				onRowsPerPageChange={handleRowsPerPageChange}
			/>
		</React.Fragment>
	);
};
