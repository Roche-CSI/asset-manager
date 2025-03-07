import React, { Fragment, useEffect, useRef, useState } from "react";
import styles from "./asset_list_table.module.scss";
import { convertToCurrentTimeZone, timeAgoString } from "../../../utils/dateUtils";
import { Link } from "react-router-dom";
import { Asset, AssetClass } from "../../../servers/asset_server";
import { PagedTable } from '../pagedTable';
import { SearchField } from "../../search";
import { CopyButton } from "../../../components/copyButton";
import { StoreNames, useStore } from "../../../stores";

const tableHeading = [
    '',
    '',
    '',
    ''
]

// const renderHead = (item: any, index: number) => <th key={index}>{item}</th>
const renderHead = (item: any, index: number, onSearch?: Function) => {
    console.log("item:", item, ", index:", index);
    return (
        <th key={index}>{
        index !== 0 ? item :
            <div className={styles.titleContainer}>
                <div className={styles.searchCard}>
                    <SearchField placeholder={"Find asset..."}
                                 onChange={(e: any) => onSearch && onSearch(e)}/>
                </div>
            </div>
        }</th>
    );
};


const renderBody = (assetClass: AssetClass, asset: Asset, index: number, project_id: string) => (
    <tr key={index}>
        {/*<td>{index + 1}</td>*/}
        <td className={styles.assetName}>
            <Link to={
                `/asset/${project_id}/${assetClass.name}/${asset.seq_id}/files?version=${asset.leafVersionNumber()}`}>
                {asset.alias?
                    <span>{asset.alias}</span>
                :
                    <div>
                        <span>{`${assetClass.name}/`}</span>
                        <span>{`${asset.seq_id}`}</span>
                    </div>
                }
            </Link>
            <CopyButton 
                textToCopy={`${assetClass.name}/${asset.alias || asset.seq_id}`}
                tooltip={"copy name"}
                styles={styles}
            />
        </td>
        <td className={styles.infoField}>{asset.leafVersion()?.commit_message}</td>
        <td>{asset.leafVersion()?.created_by}</td>
        <td className={styles.infoField}>
            {convertToCurrentTimeZone(asset.leafVersion()?.created_at, "date")}
        </td>
    </tr>
)

interface AccessData {
    lastAccessed: string;
    asset_name: string
}

interface TableProps {
    assets: Asset[];
    assetClass: AssetClass;
}

export default function AssetListTable(props: TableProps) {
    const userStore = useStore(StoreNames.userStore, true);
    let [searchKey, setSearchKey] = useState("");
    const [assets, setAssets] = useState<any>([]);
    const onSearch = (val: string) => {
        // console.log(val);
        setSearchKey(val);
    }

    useEffect(() => {
        setAssets(props.assets.sort((a1: any, a2: any) => a2.seq_id - a1.seq_id))
    }, [props.assetClass])

    return (
        <Fragment>
            <PagedTable
                limit='10'
                headData={tableHeading}
                renderHead={(item: any, index: number) => renderHead(item, index, onSearch)}
                bodyData={search(assets, searchKey)}
                renderBody={(item: any, index: number) => renderBody(props.assetClass, item, index, userStore.get("active_project"))}
                styles={styles}
            />
            {props.assets && props.assets.length === 0 &&
                <span style={{ padding: 50 }}>There are no assets in this class</span>}
        </Fragment>
    )

    function search(data: any[], searchInput?: string) {
        if (!searchInput || !data) {
            return data
        }
        let seq_id: any = null;
        let ownerOrAlias: any = null;
        // check if the user typed a number i.e. just the sequence id
        if (/^\d+$/.test(searchInput)) {
            seq_id = searchInput
        }
        // check if the user typed the full name i.e. class_name + sequence_id
        else if (searchInput.includes(props.assetClass.name)) {
            seq_id = searchInput.substring(props.assetClass.name.length);
            if (seq_id) {
                if (seq_id.startsWith("/")) {
                    seq_id = seq_id.substring(1);
                }
            }
        }
        else {
            ownerOrAlias = searchInput;
        }

        let result: any;
        if (seq_id || ownerOrAlias) {
            result = data.filter(asset => {
                if (seq_id) {
                    return String(asset.seq_id).includes(seq_id)
                }
                return String(asset.owner).includes(ownerOrAlias) || String(asset.alias).includes(ownerOrAlias)
            })
        }
        else {
            result = data;
        }
        return result;
    }
}