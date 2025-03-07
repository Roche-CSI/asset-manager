import React, {useState} from "react";
import { PagedTable } from "../pagedTable";
import styles from "./history_table.module.scss";
import {VscDiffAdded, VscDiffModified, VscDiffRemoved} from "react-icons/vsc";
import { diffItem } from "../../../servers/asset_server/assetVersion"

const renderHead = (item: any, index: number) => <th key={index}>{item}</th>

const renderBody = (item: any, index: number, path: string, onPathClick: Function) => {
    const active: boolean = path === item.path;
    const structure: string[] = item.path.split("/");
    const folderStructure: string = structure.slice(0, structure.length - 1).join("/")
    const fileName: string = structure[structure.length - 1]
    return (
        <tr key={index} className={`${styles.rowContainer} ${active? styles.active: ''}`}
                            onClick={() => onPathClick(item.path)}>
            <td className={styles.nameContainer}>
                <span className={styles.folder}>{folderStructure}</span>
                <span className={styles.filename}>
                    {folderStructure? `/${fileName}`: fileName}
                </span>
            </td>
            <td className={styles.icon}>
                {icon(item.category)}
            </td>
        </tr>
    )

}

export const icon = (category: string) => {
    switch (category) {
        case "added": return <VscDiffAdded className={`${styles.rowIcon} ${styles.cyan}`}/>;
        case "removed": return <VscDiffRemoved className={`${styles.rowIcon} ${styles.red}`}/>;
        case "altered": return <VscDiffModified className={`${styles.rowIcon} ${styles.purple}`}/>;
        case "": return "";
        default: return ""
    }
}


const versionHistory = (columns: string[], rows: object[], index: number, 
    path: string, setPath: Function, page: number, setPage: Function) => {
    return (
        <PagedTable
            limit='20'
            page={page}
            setPage={setPage}
            pageSpan={5}
            headData={columns}
            renderHead={(item: any, index: number) => renderHead(item, index)}
            bodyData={rows}
            renderBody={(item: any, index: number) => renderBody(item, index, path, setPath)}
            styles={styles}
        />
    )
}

interface TableProps {
    path: string;
    onPathClick: Function;
    diffArray: diffItem[];
}

export default function HistoryTable(props: TableProps) {
    const [page, setPage] = useState(0);

    const tableHeading: any[] = [
        // '',
        // '',
    ]

    return (
        <div>
            {versionHistory(tableHeading, props.diffArray, 0, props.path, props.onPathClick, page, setPage)}
        </div>
    )
}