import React, { useEffect, useState } from "react";
import { PagedTable } from "../pagedTable";
import styles from "./assetRef_table.module.scss";
import { convertToCurrentTimeZone } from "../../../utils";
import { AssetRef } from "../../../servers/asset_server";
import { Link } from "react-router-dom";
import { StoreNames, useStore } from "../../../stores";

const renderHead = (item: any, index: number) => <th key={index}>{item}</th>

const renderBody = (item: AssetRef, index: number, inbound: boolean, project_id: string) => {
    const [className, seq_id, version] = inbound ? item.src_version.name.split("/")
        : item.dst_version.name.split("/");
    return (
        <tr key={index}>
            <td>
                {item.id}
            </td>
            <td>
                {inbound ?
                    <Link to={`/asset/${project_id}/${className}/${seq_id}/files?version=${version}`}>
                        {item.src_version.name}
                    </Link>
                    :
                    <span>{item.src_version.name}</span>
                }
            </td>
            <td>
                {inbound ?
                    <span>{item.dst_version.name}</span>
                    :
                    <Link to={`/asset/${project_id}/${className}/${seq_id}/files?version=${version}`}>
                        {item.dst_version.name}
                    </Link>
                }
            </td>
            <td>
                {item.label}
            </td>
            <td>
                {item.created_by}
            </td>
            <td>
                {convertToCurrentTimeZone(item.created_at, "date")}
            </td>
        </tr>
    )
}

interface TableProps {
    refs: AssetRef[];
    inbound: boolean;
}

export default function AssetRefTable(props: TableProps) {
    const userStore = useStore(StoreNames.userStore, true);

    const tableHeading = [
        'ID',
        'From',
        'To',
        'Label',
        'Creator',
        'Created',
    ]

    return (
        <>
            <PagedTable
                limit='5'
                headData={tableHeading}
                renderHead={(item: any, index: number) => renderHead(item, index)}
                bodyData={props.refs}
                renderBody={(item: any, index: number) => renderBody(item, index, props.inbound, userStore.get("active_project"))}
                styles={styles}
            />
            {props.refs && props.refs.length === 0 &&
                <span style={{ padding: 50, color: "gray"}}>
                    {`This asset version has no ${props.inbound ? 'inbound' : 'outbound'} assets`}
                </span>
            }
        </>
    )
}