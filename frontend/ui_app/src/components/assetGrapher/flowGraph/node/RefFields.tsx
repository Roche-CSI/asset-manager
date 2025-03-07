import React from "react";
import { AssetRef } from "../../../../servers/asset_server";
import { convertToCurrentTimeZone } from "../../../../utils";

interface Props {
    assetRef: AssetRef | null;
}

const RefFields = (props: Props) => {
    console.log(props)
    const assetRef = props.assetRef;
    if (!assetRef) return null;

    return (
        <table className='w-full text-xs'>
            <tbody>
                <tr>
                    <td>From:</td>
                    <td>{assetRef.src_version.name}</td>
                </tr>
                <tr>
                    <td>To:</td>
                    <td>{assetRef.dst_version.name}</td>
                </tr>
                <tr>
                    <td>Label</td>
                    <td>{assetRef.label}</td>
                </tr>
                <tr>
                    <td>Creator:</td>
                    <td>{assetRef.created_by}</td>
                </tr>
                <tr>
                    <td>Created:</td>
                    <td>{convertToCurrentTimeZone(assetRef.created_at, "date")}</td>
                </tr>
            </tbody>
        </table>
    )
}

export default RefFields;
