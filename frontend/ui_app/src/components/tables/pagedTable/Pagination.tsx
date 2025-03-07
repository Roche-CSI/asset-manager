import React from "react";
import { Pagination as BsPagination } from "react-bootstrap";
import defaultStyles from "./table.module.scss";

interface paginationProps {
    currPage: number;
    totalPages: number;
    handlePageClick: Function;
    pageSpan?: number;
    styles?: any;
}

const SPAN: number = 9; // default: odd number

export default function Pagination(props: paginationProps) {
    const currPage: number = props.currPage;
    const totalPages: number = props.totalPages;
    const handlePageClick: Function = props.handlePageClick;
    const pageSpan: number = props.pageSpan ?? SPAN;
    const styles: any = props.styles ? props.styles : defaultStyles;

    if (totalPages <= 1) {
        return null;
    }
    
    const generateRange = (start: number, stop: number, step: number = 1): number[] =>
        Array.from({ length: (stop - start) / step }, (_, i) => start + (i * step))

    const generateActiveRange = (): number[] => {
        let active: number = pageSpan - 4;
        let start: number;
        if (currPage <= Math.floor(active / 2)) {
            start = 0
        } else if (currPage >= totalPages - Math.floor(active / 2)) {
            start = totalPages - active
        } else {
            start = currPage - Math.floor(active / 2)
        }
        return generateRange(start, Math.min(start + active, totalPages))
    }

    const NearEndPagination = () => {
        let items: any[] = [];
        let numOfEachEnd: number = Math.floor(pageSpan / 2)
        const paginationItem = (num: number) => (
            <BsPagination.Item key={num} active={num === currPage} onClick={() => handlePageClick(num)}>
                {num + 1}
            </BsPagination.Item>
        )
        for (let num = 0; num < Math.min(numOfEachEnd, totalPages); num++) {
            items.push(paginationItem(num));
        }
        if (totalPages > numOfEachEnd) {
            if (totalPages > numOfEachEnd + 1) {
                items.push(<BsPagination.Ellipsis key={totalPages} disabled />)
            }
            for (let num = Math.max(totalPages-numOfEachEnd, numOfEachEnd); num < totalPages; num++) {
                items.push(paginationItem(num));
            }    
        }
        return (
            <BsPagination size="sm" className={styles.tablePagination}>
                {currPage !== 0 ? <BsPagination.Prev onClick={() => handlePageClick(currPage - 1)} />
                    : <BsPagination.Prev disabled />}
                {items}
                {currPage !== totalPages - 1 ?
                    <BsPagination.Next onClick={() => handlePageClick(currPage + 1)} /> : <BsPagination.Next disabled />}
            </BsPagination>
        )
    }

    const CenterPagination = () => {
        let activePages: number[] = generateActiveRange();
        return (
            <BsPagination size="sm" className={styles.tablePagination}>
                {currPage !== 0 ? <BsPagination.Prev onClick={() => handlePageClick(currPage - 1)} />
                    : <BsPagination.Prev disabled />}
                {currPage >= Math.floor(pageSpan / 2) ? <BsPagination.Item onClick={() => handlePageClick(0)}>{1}</BsPagination.Item> : null}
                {currPage >= Math.floor(pageSpan / 2) ? <BsPagination.Ellipsis disabled /> : null}
                {activePages.map((item, index) => (
                    <BsPagination.Item key={index} onClick={() => handlePageClick(item)} active={currPage === item}>
                        {item + 1}
                    </BsPagination.Item>)
                )}
                {currPage <= totalPages - Math.ceil(pageSpan / 2) ? <BsPagination.Ellipsis disabled /> : null}
                {currPage <= totalPages - Math.ceil(pageSpan / 2) ? <BsPagination.Item onClick={() => handlePageClick(totalPages - 1)}>{totalPages}</BsPagination.Item> : null}
                {currPage !== totalPages - 1 ?
                    <BsPagination.Next onClick={() => handlePageClick(currPage + 1)} /> : <BsPagination.Next disabled />}
            </BsPagination>
        )
    }

    let isNearEnd: boolean = (currPage < Math.floor(pageSpan / 2)) || (currPage > totalPages - Math.ceil(pageSpan / 2))
    return (
        <div>
            {isNearEnd ? <NearEndPagination /> : <CenterPagination />}
        </div>
    )
}