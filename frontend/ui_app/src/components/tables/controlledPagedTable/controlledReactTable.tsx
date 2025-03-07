import React, { useMemo } from "react";
import {
    useReactTable,
    getCoreRowModel,
    ColumnDef,
    OnChangeFn,
    PaginationState,
    FilterFn,
} from '@tanstack/react-table';
import {
    RankingInfo,
    rankItem,
} from '@tanstack/match-sorter-utils'


import Pagination from "./pagination/pagination";
import ReactTable from "./table/reactTable";

export interface PageData {
    data: any[];
    pageCount: number;
}

interface Props {
    pageData: PageData;
    pagination: PaginationState;
    setPagination: OnChangeFn<PaginationState>;
    columns: ColumnDef<any>[];
    TheadComponent?: any;
    styles?: any;
}

declare module '@tanstack/table-core' {
    interface FilterFns { fuzzy: FilterFn<unknown> }
    interface FilterMeta { itemRank: RankingInfo }
}

const fuzzyFilter: FilterFn<any> = (row, columnId, value, addMeta) => {
    // Rank the item
    const itemRank = rankItem(row.getValue(columnId), value)

    // Store the itemRank info
    addMeta({
        itemRank,
    })

    // Return if the item should be filtered in/out
    return itemRank.passed
}


const ControlledReactTable = (props: Props) => {
    const { columns, pageData, pagination, setPagination, styles } = props;
    const { data, pageCount } = pageData;

    const columnData = useMemo(() => columns, [columns]);
    const rowData = useMemo(() => data, [data]);

    const table = useReactTable({
        data: rowData,
        columns: columnData,
        pageCount: pageCount ?? -1,
        state: {
            pagination,
        },
        onPaginationChange:  setPagination,
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
        filterFns: {
            fuzzy: fuzzyFilter,
        },
    })

    return (
        <div className={styles?.container}>
            <ReactTable table={table} TheadComponent={props.TheadComponent} styles={styles} />
            <Pagination table={table} styles={styles} />
        </div>
    );
};

export default ControlledReactTable;