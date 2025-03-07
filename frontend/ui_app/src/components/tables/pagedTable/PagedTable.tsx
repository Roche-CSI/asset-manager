import React, {useCallback, useEffect, useMemo, useState} from 'react'
import defaultStyles from "./table.module.scss";
import Pagination from "./Pagination";

interface TableProps {
    limit?: string;
    headData: any[];
    renderHead: Function;
    bodyData: object[];
    renderBody: Function;
    styles?: any;
    pageSpan?: number;
    page?: number;
    setPage?: Function;
}

const LIMIT: number = 10;

export default function PagedTable(props: TableProps) {

    const totalPages = useMemo((): number => {
        const items: object[] = props.bodyData;
        const itemsPerPage: number = Number(props.limit) || LIMIT;
        return items? Math.ceil(items.length / itemsPerPage): 0;
    }, [props.bodyData, props.limit])

    const getCurrentItems = useCallback((page: number) => {
        const items: object[] = props.bodyData;
        const itemsPerPage: number = Number(props.limit) || LIMIT;
        const start: number = itemsPerPage * page
        const end: number = start + itemsPerPage
        return items.slice(start, end)
    }, [props.bodyData, props.limit])
    
    const [currPage, setCurrPage] = useState<number>(props.page || 0);
    const [dataShow, setDataShow] = useState<object[]>(getCurrentItems(props.page || 0));

    useEffect(() => {
        setCurrPage(props.page || 0)
        setDataShow(getCurrentItems(props.page || 0))
    }, [props.bodyData, props.page, props.limit, getCurrentItems])

    const handlePageClick = (page: number) => {
        if (currPage < 0 || currPage === page) {
            return;
        }
        setCurrPage(page);
        props.setPage && props.setPage(page);
        const currentItems: object[] = getCurrentItems(page);
        setDataShow(currentItems)
    }
    
    const styles = props.styles ? props.styles : defaultStyles;
    return (
        <div>
            <div className={styles.tableWrapper} style={{padding: "0px"}}>
                <table>
                    {
                        props.headData && props.renderHead ? (
                            <thead>
                            <tr>
                                {props.headData.map((item: any, index: number) => props.renderHead(item, index))}
                            </tr>
                            </thead>
                        ) : null
                    }
                    {
                        props.bodyData && props.renderBody ? (
                            <tbody>
                            {dataShow.map((item: any, index: number) => props.renderBody(item, index))}
                            </tbody>
                        ) : null
                    }
                </table>
                <div>
                    <Pagination currPage={currPage}
                                totalPages={totalPages}
                                pageSpan={props.pageSpan}
                                handlePageClick={handlePageClick}
                                styles={styles}/>
                </div>
            </div>
        </div>
    )

}
