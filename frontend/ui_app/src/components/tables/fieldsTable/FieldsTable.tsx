import React, {useState} from "react";
import {Table} from "../table";
import styles from "./table.module.scss";

const renderHead = (item: any, index: number) => <th key={index}>{item}</th>

const renderBody = (item: any, index: number) => (
    <tr key={index}>
        <td>
            {/*<Link to={`/asset/${item.asset_class.name}/${item.seq_id}/files`}>*/}
            {/*    {`${item.asset_class.name}/${item.seq_id}`}*/}
            {/*</Link>*/}
            {item[0]}
        </td>
        <td>{item[1]}</td>
    </tr>
)

interface AssetFieldsTableProps {
    title?: any;
    fields: any[];
}

export default function FieldsTable(props: AssetFieldsTableProps) {
    /***
     * displays a list of fields in tabular format
     */
    const tableHeading = [
        props.title[0] || 'description',
        props.title[1] || "",
    ]

    return (
        <div>
            <Table
                limit='10'
                headData={tableHeading}
                renderHead={(item: any, index: number) => renderHead(item, index)}
                bodyData={props.fields}
                renderBody={(item: any, index: number) => renderBody(item, index)}
                styles={styles}
            />
            <br/>
        </div>
    )
}