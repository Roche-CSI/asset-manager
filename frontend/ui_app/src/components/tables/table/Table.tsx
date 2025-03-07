import React, {useEffect, useState} from 'react'
import defaultStyles from "./table.module.scss";

interface TableProps {
    limit: string;
    headData: any[];
    renderHead: Function;
    bodyData: object[];
    renderBody: Function;
    styles?: any;
    page?: number
}

const displayRows = (limit: number, data: any[]) => {
    return limit && data ? data.slice(0, Number(limit)) : data;
}

export default function Table(props: TableProps) {
    const [dataShow, setDataShow] = useState(displayRows(Number(props.limit), props.bodyData));
    // change dataShow when props changes
    useEffect(() => {
        setDataShow(displayRows(Number(props.limit), props.bodyData))
        if (props.page != undefined) {
            console.log("props-page:", props.page);
            setCurrPage(props.page);
        }
    }, [props.bodyData]);
    // console.log("bodyData: ", props.bodyData, " dataShow: ", dataShow, "initDataShow: ", initDataShow);
    let pages: number = 1;
    let range: any[] = []

    if (props.limit !== undefined) {
        let page = Math.floor(props.bodyData.length / Number(props.limit))
        pages = props.bodyData.length % Number(props.limit) === 0 ? page : page + 1
        // @ts-ignore
        range = [...Array(pages).keys()];
    }

    const [currPage, setCurrPage] = useState(0)

    const selectPage = (page: number) => {
        const start = Number(props.limit) * page
        const end = start + Number(props.limit)
        setDataShow(props.bodyData.slice(start, end))
        setCurrPage(page)
    }
    console.log("curr-page:", currPage);
    const styles = props.styles ? props.styles : defaultStyles;
    return (
        <div>
            <div className={styles.tableWrapper}>
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
            </div>
            {
                pages > 1 ? (
                    <div className={styles.tablePagination}>
                        {
                            range.map((item, index) => (
                                <div key={index} className={`${styles.tablePaginationItem} ${currPage === index ? styles.active : ''}`} onClick={() => selectPage(index)}>
                                    {item + 1}
                                </div>
                            ))
                        }
                    </div>
                ) : null
            }
        </div>
    )
}