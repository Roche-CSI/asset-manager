import React, { useEffect, useMemo, useState } from 'react';
import { Pagination } from '../../datagrid/Pagination';

interface TableProps {
    itemsPerPage?: number;
    headData: any[];
    renderHead: (item: any, index: number) => React.ReactNode;
    bodyData: any[];
    renderBody: (item: any, index: number) => React.ReactNode;
    page?: number;
    setPage?: (page: number) => void;
    className?: string;
}

const DEFAULT_ROWS_PER_PAGE = 10;

export default function PagedTable(props: TableProps) {
    const [rowsPerPage, setRowsPerPage] = useState<number>(props.itemsPerPage || DEFAULT_ROWS_PER_PAGE);
    const [currentPage, setCurrentPage] = useState<number>(props.page || 1);

    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;

    const totalPages = useMemo((): number => {
        const items = props.bodyData || [];
        return Math.ceil(items.length / rowsPerPage);
    }, [props.bodyData, rowsPerPage]);

    const paginatedData = useMemo(() => {
        const items = props.bodyData || [];
        return items.slice(startIndex, endIndex);
    }, [props.bodyData, startIndex, endIndex]);

    useEffect(() => {
        if (props.page && props.page !== currentPage) {
            setCurrentPage(props.page);
        }
    }, [props.page, currentPage]);

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        if (props.setPage) {
            props.setPage(page);
        }
    };

    const handleRowsPerPageChange = (newRowsPerPage: number) => {
        setRowsPerPage(newRowsPerPage);
        setCurrentPage(1); // Reset to first page if rows per page changes
    };

    return (
        <div className={`w-full ${props.className || ''}`}>
            <div className='w-full border border-slate-200 rounded-lg'>
                <table className="table-fixed w-full">
                    {props.headData && props.renderHead && (
                        <thead>
                            <tr>
                                {props.headData.map((item, index) => props.renderHead(item, index))}
                            </tr>
                        </thead>
                    )}
                    {props.bodyData && props.renderBody && (
                        <tbody>
                            {paginatedData.map((item, index) => props.renderBody(item, index))}
                        </tbody>
                    )}
                </table>
                {!props.bodyData || props.bodyData.length === 0 &&
                <div className="h-24 w-full">
                    <div className="flex justify-center items-center h-full text-neutral-500">
                        No data available
                    </div>
                </div>
            }
            </div>
            <Pagination
                startIndex={startIndex + 1}
                endIndex={Math.min(endIndex, props.bodyData.length)}
                totalCount={props.bodyData.length}
                totalPages={totalPages}
                currentPage={currentPage}
                onPageChange={handlePageChange}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleRowsPerPageChange}
            />
        </div>
    );
}