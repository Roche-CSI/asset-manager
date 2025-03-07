import React, {useEffect, useState} from "react";
import {Asset, AssetObject} from "../servers/asset_server";
import {AssetFormatter} from "../servers/asset_server/formatter";
import {isEmptyObject} from "../utils";
import {Table, Dropdown, DropdownButton} from 'react-bootstrap';
import {DropDownMenu} from "../components";
import {AssetVersion} from "../servers/asset_server/assetVersion";


export default function AssetViewer(props: any) {
    const [asset, setAsset] = useState({});
    useEffect(() => {
        Asset.getFromServer(props.asset_id).then((json) => {
            let new_asset = new Asset(json);
            console.log(new_asset);
            setAsset(new_asset);
        })
    }, [])

    return (
        <div>
            {isEmptyObject(asset) ? "Loading": <AssetTable asset={asset as Asset}/>}
        </div>
    );
}

interface AssetTableProps {
    asset: Asset;
}

function AssetTable(props: AssetTableProps) {

    let [activeVersion, setActiveVersion] = useState(props.asset.leaf_version_id)

    let data: object  = new AssetFormatter(props.asset).assetFields();
    let rows = Object.keys(data).map((key, indx) => {
        return (
            <tr key={indx}>
                <td>{key}</td>
                <td>{AssetField((data as any)[key])}</td>
            </tr>
        )
    })

    const changeVersion = (version: string) => {
        setActiveVersion(parseInt(version));
    }
    const options = props.asset.versions.map((version) => {
        return {eventKey: version.id, value: version.number}
    })
    console.log("active version is:", activeVersion);

    let version = props.asset.getVersion(null, activeVersion) as AssetVersion;
    if (!version.objects || version.objects.length === 0) {
        let object_ids: Set<string> = AssetVersion.resolveVersions(props.asset.versions, version);
        let objects = new Set<any>();
        object_ids.forEach((id) => {
            objects.add(props.asset.all_objects[id]);
        })
        version.objects = Array.from(objects);
    }
    let object_rows = version.objects.map((obj, idx) => {
        return (
            <tr key={idx}>
                <td>{idx}</td>
                <td>{(obj as AssetObject).path()}</td>
            </tr>
        )
    })

    return (
        <div>
            <Table striped bordered hover>
                <tbody>
                {rows}
                </tbody>
            </Table>
            <DropDownMenu options={options} onSelect={changeVersion}/>
            <Table striped bordered hover>
                <tbody>
                {object_rows}
                </tbody>
            </Table>
        </div>
    )
}

function AssetField(value: any) {
    if (typeof value == "string") {
        return <span>{value}</span>
    }
    else if (value instanceof Array) {
        return <DropDownMenu options={value as []}/>
    }
}