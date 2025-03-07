import React, { useEffect, useState } from "react";
import { PaginationState } from '@tanstack/react-table';

import usePagination from "../controlledPagedTable/pagination/usePagination";
import useColumns from "./tableColumn/useColumns";
import useSearchTerms from "./useSearch/useSearch";
import SearchForm, { SearchObject } from "./useSearch/searchForm";
import SearchStatus from "./useSearch/searchStatus";

import { AssetClass } from "../../../servers/asset_server";
import ControlledReactTable, { PageData } from "../controlledPagedTable/controlledReactTable";
import useDidMountEffect from "../../commonHooks/useDidMountEffect";

import styles from "./asset_list_table.module.scss";

interface TableProps {
    pageData: PageData;
    assetClass: AssetClass;
    fetchAssetsFromServer?: Function;
}

export interface AssetSearchTerms {
    owner?: string;
    alias?: string;
    seq_id?: string;
    search_by?: string;
    pageNumber?: number;
    pageSize?: number;
}

export default function AssetListControlledTable(props: TableProps) {
    const { pagination, setPagination } = usePagination({ pageSize: 10 })
    const { pageIndex, pageSize }: PaginationState = pagination
    const [searchKey, setSearchKey] = useState("");
    const [searchList, setSearchList] = useState<SearchObject[]>([]);
    const { searchTermsRef, setSearchTerms } = useSearchTerms()

    const getSearchTerms = (newSearchList: SearchObject[]) => {
        let terms: any = { pageIndex: pageIndex, pageSize: pageSize, search_by: searchKey }
        newSearchList.forEach((term: any, idx: number) => { terms[term.key] = term.value })
        if ("owner" in terms || "alias" in terms || "seq_id" in terms) {
            delete terms["search_by"]
        }
        return terms
    }

    useDidMountEffect(() => {// fetch assets when page changes, but not on initial render
        let terms: AssetSearchTerms = getSearchTerms(searchList)
        props.fetchAssetsFromServer && props.fetchAssetsFromServer(terms)
    }, [pageIndex])

    const handleSearch = (newSearchList: SearchObject[]) => {
        let terms: AssetSearchTerms = getSearchTerms(newSearchList)
        if (newSearchList.length === 0 && !searchKey) {
            terms = { ...terms, "pageNumber": 0 }
            setPagination({ pageIndex: 0, pageSize: pageSize })
        }
        setSearchList(newSearchList)
        props.fetchAssetsFromServer && props.fetchAssetsFromServer(terms)
        setSearchTerms(terms)
    }

    const assetListColumns = useColumns({ assetClass: props.assetClass, searchRef: searchTermsRef })

    return (
        <div>
            <div className='flex flex-col justify-start w-full px-2.5 mt-2.5'>
                <SearchForm searchKey={searchKey} setSearchKey={setSearchKey}
                    onSubmit={handleSearch} />
                <SearchStatus searchList={searchList} setSearchList={setSearchList}
                    handleSearch={handleSearch} />
            </div>
            <ControlledReactTable
                pageData={props.pageData}
                pagination={pagination}
                setPagination={setPagination}
                columns={assetListColumns}
                TheadComponent={() => null}
                styles={styles}
            />
        </div>
    )
}