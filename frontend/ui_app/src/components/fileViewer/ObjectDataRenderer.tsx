import React from "react";
import styles from "./renderer.module.scss";
import {AssetObject} from "../../servers/asset_server";
import {isEmptyObject} from "../../utils";
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import DocumentScannerOutlinedIcon from '@mui/icons-material/DocumentScannerOutlined';
import PatternOutlinedIcon from '@mui/icons-material/PatternOutlined';
import ShareOutlinedIcon from '@mui/icons-material/ShareOutlined';
import MiscellaneousServicesOutlinedIcon from '@mui/icons-material/MiscellaneousServicesOutlined';
import { StoreNames, useStore } from "../../stores";

interface Props {
    objectData: object;
}

export default function ObjectDataRenderer(props: Props) {
    const userStore = useStore(StoreNames.userStore);

    if(!props.objectData) {
        return null;
    }
    const obj = new AssetObject(props.objectData);
    const [hashType, hashValue] = obj.content.hash();
    return (
        <div className={`${styles.wrapper}`}>
            <div className={styles.field}>
                <DocumentScannerOutlinedIcon/>
                <div>{obj.path()}</div>
            </div>
            <div className={styles.field}>
                <MiscellaneousServicesOutlinedIcon/>
                <div>
                    <span className={styles.badge}>
                       {obj.content.size && obj.content.size.toLocaleString("en-US")}
                    </span>
                    <span>kB</span>
                </div>
            </div>
            <div className={styles.field}>
                <AccessTimeIcon/>
                <div>{obj.created_at}</div>
            </div>
            <div className={styles.field}>
                <AccountCircleIcon/>
                <div>{obj.created_by}</div>
            </div>
            <div className={styles.field}>
                <PatternOutlinedIcon/>
                <div>
                    <span className={styles.badge}>{hashType}</span>
                    <span>{hashValue}</span>
                </div>
            </div>
            {meta(obj)}
        </div>
    );

    function meta(obj: any) {
        if(!obj || isEmptyObject(obj)) {
            return null
        }
        return (
            <React.Fragment>
                <div className={styles.field}>
                    <ShareOutlinedIcon/>
                    <div>
                        <a href={srcURL(obj.content.meta.src, hashValue)} target={"_blank"}>
                            {obj.content.meta.src}
                        </a>
                    </div>
                </div>
            </React.Fragment>
        )
    }

    function srcURL(src: string, hash: string) {
        if (!src) {
            return "";
        }
        if (src.startsWith("us.gcr.io") || src.startsWith("gcr.io")) {
            const prefix = userStore.get('dashboard_settings')?.gcr_prefix || "https://console.cloud.google.com/gcr/images/";
            let model: string = (src.split("/").pop() as string);
            let shaId = "sha256:";
            if (model.includes(shaId)) {
                let [modelName, hash] = model.split(shaId);
                return `${prefix}/${modelName}@${shaId}${hash}`
            }else {
                let tagSep = ":";
                let [modelName, tag] = model.split(tagSep);
                return `${prefix}/${modelName}@${shaId}${hash}`
            }
        }
        return src;
    }
}
