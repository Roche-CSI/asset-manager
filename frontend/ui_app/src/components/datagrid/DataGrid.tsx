/* eslint-disable no-mixed-spaces-and-tabs */
import React, {useMemo, useState} from 'react';
import {max} from "lodash";
import {Pagination} from "./Pagination";

export interface DataCardProps<T> {
	item: T;
	routeGenerator?: (resource: string, id: string) => string;
}

export interface RouteGenerator {
	(resource: string, id: string): string;
}


interface GridProps<T> {
	items: T[];
	// renderCard: (item: T, index: number) => React.ReactNode;
	itemCard: React.FC<DataCardProps<T>>;
	routeGenerator?: RouteGenerator
	className?: string;
	cols?: number;
	onPageChange?: (page: number) => void;
	onRowsPerPageChange?: (rowsPerPage: number) => void;
	selfPagination?: boolean; // If true, the component will handle pagination, set to false if you are fetching data from server
}

export const DataGrid = <T, >({
	                              items,
	                              itemCard,
	                              className,
	                              routeGenerator,
	                              cols = 3,
	                              onPageChange,
	                              onRowsPerPageChange,
	                              selfPagination
                              }: GridProps<T>) => {
	const [rowsPerPage, setRowsPerPage] = useState<number>(10);
	const [currentPage, setCurrentPage] = useState<number>(1);
	const startIndex = max([(currentPage - 1) * rowsPerPage, 0]);
	const endIndex = startIndex! + rowsPerPage;
	
	// Calculate the paginated data
	const paginatedData = useMemo(() => {
			return selfPagination ? items : items.slice(startIndex, endIndex);
		},
		[items, currentPage, rowsPerPage]
	);
	
	const handlePageChange = (page: number) => {
		setCurrentPage(page);
		onPageChange && onPageChange(page);
	};
	
	const handleRowsPerPageChange = (rowsPerPage: number) => {
		// check if the current page is valid
		const totalPages = Math.ceil(items.length / rowsPerPage);
		if (currentPage > totalPages) {
			setCurrentPage(totalPages);
		}
		setRowsPerPage(rowsPerPage);
		onRowsPerPageChange && onRowsPerPageChange(rowsPerPage);
	}
	
	const DataCard = itemCard;
	// console.log("paginatedData", JSON.stringify(paginatedData));
	return (
		<React.Fragment>
			<div className={`grid gap-4 grid-cols-1 lg:grid-cols-${cols - 1} 2xl:grid-cols-${cols} ${className}`}>
				{paginatedData.map((item, index) => <DataCard
					key={index}
					item={item}
					routeGenerator={routeGenerator}/>)}
			</div>
			<Pagination startIndex={startIndex! + 1}
			            endIndex={endIndex}
			            totalCount={items.length}
			            totalPages={Math.ceil(items.length / rowsPerPage)}
			            currentPage={currentPage}
			            onPageChange={handlePageChange}
			            rowsPerPage={rowsPerPage}
			            onRowsPerPageChange={handleRowsPerPageChange}/>
		</React.Fragment>
	
	);
	
};
