import React from "react";
import {Table} from "../table";
import styles from "./table.module.scss";
import customerList from "../../../assets/data/customer-list.json";

const customerTableHead = [
    '',
    'name',
    'email',
    'phone',
    'total orders',
    'total spend',
    'location'
]

const renderHead = (item: any, index: number) => <th key={index}>{item}</th>

const renderBody = (item: any, index: number) => (
    <tr key={index}>
        <td>{item.id}</td>
        <td>{item.name}</td>
        <td>{item.email}</td>
        <td>{item.phone}</td>
        <td>{item.total_orders}</td>
        <td>{item.total_spend}</td>
        <td>{item.location}</td>
    </tr>
)

export default function PersonTable(props: any) {

    return (
        <Table
            limit='10'
            headData={customerTableHead}
            renderHead={(item: any, index: number) => renderHead(item, index)}
            bodyData={customerList}
            renderBody={(item: any, index: number) => renderBody(item, index)}
        />
    )
}