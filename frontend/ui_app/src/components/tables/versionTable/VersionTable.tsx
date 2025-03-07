import React, {useState} from "react";
import {Table} from "../table";
import styles from "./version_table.module.scss";
import historyJson from "../../../assets/data/history-data.json";
import {convertToCurrentTimeZone, daysAgo} from "../../../utils";
import {Link, useLocation} from "react-router-dom";
import {VscDiffAdded, VscDiffModified, VscDiffRemoved} from "react-icons/vsc";
import {useQuery} from "../../../utils/utils";
import {AccessTime, AccountCircleOutlined, TopicOutlined} from "@mui/icons-material";
import {BiAt} from "react-icons/bi";
import {AssetVersion} from "../../../servers/asset_server/assetVersion";
import {Asset} from "../../../servers/asset_server";

const tableHeading = [
    'versions',
    '',
    // 'files added',
    // 'files removed',
    // 'files altered'
]

const renderHead = (item: any, index: number) => <th key={index}>{item}</th>

const icon = (item: any) => {
    switch (true) {
        case item.added:
            return <VscDiffAdded className={`${styles.rowIcon} ${styles.cyan}`}/>;
        case item.removed:
            return <VscDiffRemoved className={`${styles.rowIcon} ${styles.red}`}/>;
        case item.altered:
            return <VscDiffModified className={`${styles.rowIcon} ${styles.purple}`}/>;
        default:
            return null
    }
}

interface TableProps {
    asset: Asset;
}


export default function VersionTable(props: TableProps) {
    const location = useLocation();
    const query = useQuery();
    // console.log("location: ", location, 'query: ', query.get('version'));
    let rows: any[] = []
    for (let index in props.asset.versions) {
        let data = (props.asset.versions[index] as any);
        rows.push({
            number: data.number,
            route: `${location.pathname}?version=${data.number}`,
            active: Boolean(data.number === query.get("version")),
            commit_hash: data.commit_hash,
            commit_message: data.commit_message,
            created_by: data.created_by,
            created_at: data.created_at
        })
    }

    const versionHistory = (columns: string[], rows: object[], index: number) => {
        return (
            <Table
                key={index}
                limit='10'
                headData={columns}
                renderHead={(item: any, index: number) => renderHead(item, index)}
                bodyData={rows}
                renderBody={(item: any, index: number) => renderBody(item, index)}
                styles={styles}
                page={0}
            />
        )
    }

    const renderBody = (item: any, index: number) => {
        // const Icon: any = icon(item);
        // console.log(Icon);
        return (
            <tr key={index}>
                <td>
                    <Link to={item.route} className={styles.link}>
                        {/*<span>{item.number}</span>*/}
                        {getRow(item)}
                    </Link>
                </td>
            </tr>
        )
    }

    return (
        <div>
            {versionHistory(tableHeading, rows, 0)}
        </div>
    )

    function getRow(item: any) {
        return (
            <div className={`${styles.rowCard} ${item.active ? styles.active : ''}`}>
                <div className={styles.rowItem}>
                    <span>{item.number}</span>
                    <span>{item.commit_message}</span>
                </div>
                <div className={styles.rowItem}>
                    {item.created_by}
                </div>
                <div className={styles.rowItem}>
                    {convertToCurrentTimeZone(item.created_at, "date")}
                </div>
                <div className={styles.rowItem}>{item.commit_hash}</div>
            </div>)
    }
}