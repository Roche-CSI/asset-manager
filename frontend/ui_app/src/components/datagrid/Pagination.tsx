import React, { ChangeEvent } from "react";

interface PaginationProps {
	startIndex: number;
	endIndex: number;
	totalCount: number;
	totalPages: number;
	currentPage: number;
	onPageChange: (page: number) => void;
	rowsPerPage: number;
	onRowsPerPageChange: (rowsPerPage: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
	                                                      startIndex,
	                                                      endIndex,
	                                                      totalCount,
	                                                      totalPages,
	                                                      currentPage,
	                                                      onPageChange,
	                                                      rowsPerPage,
	                                                      onRowsPerPageChange
                                                      }) => {
	
	const handlePageChange = (page: number) => {
		if (page >= 1 && page <= totalPages) {
			onPageChange(page);
		}
	};
	
	const handleRowsPerPageChange = (event: ChangeEvent<HTMLSelectElement>) => {
		onRowsPerPageChange(parseInt(event.target?.value, 10));
	};
	
	const getPageNumbers = () => {
		const pageNumbers = [];
		const totalPageButtons = 7; // Adjust this number to show more or fewer page buttons
		const sidePages = Math.floor((totalPageButtons - 3) / 2); // Pages to show on each side of current page
		
		if (totalPages <= totalPageButtons) {
			// If total pages are less than or equal to totalPageButtons, show all pages
			for (let i = 1; i <= totalPages; i++) {
				pageNumbers.push(i);
			}
		} else {
			// Always add first page
			pageNumbers.push(1);
			
			if (currentPage - sidePages > 2) {
				pageNumbers.push('...');
			}
			
			// Add pages around current page
			const start = Math.max(2, currentPage - sidePages);
			const end = Math.min(totalPages - 1, currentPage + sidePages);
			for (let i = start; i <= end; i++) {
				pageNumbers.push(i);
			}
			
			if (currentPage + sidePages < totalPages - 1) {
				pageNumbers.push('...');
			}
			
			// Always add last page
			pageNumbers.push(totalPages);
		}
		
		return pageNumbers;
	};
	
	return (
		<div className="flex items-center justify-between border-t border-base-300 py-3 mt-6">
			{/* Mobile view buttons (unchanged) */}
			<div className="flex flex-1 justify-between sm:hidden">
				{/* ... (previous and next buttons for mobile) */}
			</div>
			
			<div className="sm:flex sm:flex-1 sm:items-center sm:justify-between">
				<div>
					<p className="text-sm text-gray-700">
						Showing
						<span className="font-medium m-1">{startIndex}</span>
						to
						<span className="font-medium m-1">{Math.min(endIndex + 1, totalCount)}</span>
						of
						<span className="font-medium m-1 ">{totalCount}</span>
						results
					</p>
				</div>
				<div className="flex items-center justify-between ">
					<div className="mr-4">
						<label htmlFor="rows-per-page" className="text-sm font-medium text-gray-700">
							Items per page:
						</label>
						<select
							id="rows-per-page"
							value={rowsPerPage}
							onChange={handleRowsPerPageChange}
							className="ml-2 border border-base-300 rounded-md py-1 px-2 text-gray-900 cursor-pointer"
						>
							<option value={5}>5</option>
							<option value={10}>10</option>
							<option value={15}>15</option>
							<option value={20}>20</option>
						</select>
					</div>
					<div>
						<nav className="isolate inline-flex -space-x-px rounded-md cursor-pointer" aria-label="Pagination">
							<a
								onClick={() => handlePageChange(currentPage - 1)}
								className={`relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-base-300 hover:bg-base-200 focus:z-20 focus:outline-offset-0 ${currentPage === 1 ? 'cursor-not-allowed' : ''}`}
							>
								<span className="sr-only">Previous</span>
								<svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
									<path fillRule="evenodd"
									      d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
									      clipRule="evenodd" />
								</svg>
							</a>
							{getPageNumbers().map((page, index) => (
								page === '...' ? (
									<span key={`ellipsis-${index}`} className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-700 ring-1 ring-inset ring-base-300">
                    ...
                  </span>
								) : (
									<a
										key={page}
										onClick={() => handlePageChange(page as number)}
										className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${page === currentPage ? 'bg-neutral-400 text-white' : 'text-neutral-500 ring-1 ring-inset ring-base-300 hover:bg-base-100'} focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-base-300`}
										aria-current={page === currentPage ? 'page' : undefined}
									>
										{page}
									</a>
								)
							))}
							<a
								onClick={() => handlePageChange(currentPage + 1)}
								className={`relative inline-flex items-center rounded-r-md px-2 py-2 text-neutral-400 ring-1 ring-inset ring-base-300 hover:bg-base-100 focus:z-20 focus:outline-offset-0 ${currentPage === totalPages ? 'cursor-not-allowed' : ''}`}
							>
								<span className="sr-only">Next</span>
								<svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
									<path fillRule="evenodd"
									      d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
									      clipRule="evenodd" />
								</svg>
							</a>
						</nav>
					</div>
				</div>
			</div>
		</div>
	);
}
