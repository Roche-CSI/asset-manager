import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Table } from "../table";
import { SearchField } from "../../search";
import styles from "./class_table.module.scss";
import { convertToCurrentTimeZone } from "../../../utils";
import { AccessTime, AccountCircleOutlined, TopicOutlined } from "@mui/icons-material";
import { AssetClass } from "../../../servers/asset_server";
import AddIcon from '@mui/icons-material/Add';
import Tooltip from '@mui/material/Tooltip';
import { Button } from "react-bootstrap";

const tableHeading = [
    // '',
    'name',
    // '# assets',
    // 'owner',
    // 'created by',
    // 'created at'
]

const renderHead = (item: any, index: number, onSearch?: Function, onCreate?: Function) =>
    <th key={index}>
        <div className={styles.titleContainer}>
            {
                item === "name" ?
                    <div className={styles.searchCard}><SearchField placeholder={"Find asset class..."}
                                                                    onChange={(e: any) => onSearch && onSearch(e)}/>
                    </div>
                    : item
            }
            <Tooltip title="Create Asset Class" placement={"top"}>
                <Button variant={"primary"} onClick={() => onCreate && onCreate()}>
                    <AddIcon className={styles.createButton} />
                    <span>Create</span>
                </Button>
                {/*<IconButton onClick={() => onCreate && onCreate()}>*/}
                {/*    <AddCircleIcon className={styles.createButton}/>*/}
                {/*</IconButton>*/}
            </Tooltip>
        </div>
    </th>;

const tableRow = (item: AssetClass, index: number, projectId: string) =>
    <tr key={index}>
        <td>
            <div key={index} className={styles.rowCard}>
                <div className={styles.rowTitle}>
                    <Link to={`/asset_class?project_id=${projectId}&name=${item.name}`} className={styles.link}>
                        {item.title}
                    </Link>
                    <div className={styles.rowTitleSubText}>{item.name}</div>
                </div>
                <div className={styles.rowBody}>{item.description}</div>
                <div className={styles.rowFooter}>
                    <div className={styles.rowFooterItem}>
                        <AccountCircleOutlined className={`${styles.rowFooterIcon} ${styles.cyan}`} />
                        <span>{item.owner}</span>
                    </div>
                    <div className={styles.rowFooterItem}>
                        <AccessTime className={`${styles.rowFooterIcon} ${styles.red}`} />
                        <span>{convertToCurrentTimeZone(item.created_at, "date")}</span>
                    </div>
                    <div className={styles.rowFooterItem}>
                        <TopicOutlined className={`${styles.rowFooterIcon} ${styles.purple}`} />
                        <span>{item.counter} {item.counter > 1 ? 'assets' : 'asset'}</span>
                    </div>

                </div>
            </div>
        </td>
    </tr>


interface TableProps {
    classList: AssetClass[],
    projectId: string
    onCreate?: Function
}


export default function ClassListTable(props: TableProps) {

    let [searchKey, setSearchKey] = useState("");
    const onSearch = (val: string) => {
        // console.log(val);
        setSearchKey(val);
    }

    const onCreate = () => {
        //console.log("on create");
        props.onCreate && props.onCreate();
    }

    const classList = props.classList;

    return (
        <Table
            limit='10'
            headData={tableHeading}
            renderHead={(item: any, index: number) => renderHead(item, index, onSearch, onCreate)}
            bodyData={search(classList, searchKey)}
            renderBody={(item: any, index: number) => tableRow(item, index, props.projectId)}
            styles={styles}
        />
    )

    function search(data: any[], searchInput?: string) {
        if (!searchInput) {
            return data;
        }
        let filteredData = data.filter(assetClass => {
            return (
                assetClass.name.toLowerCase().includes(searchInput.toLowerCase())
            );
        });
        // console.log(filteredData);
        return filteredData;
    };

}