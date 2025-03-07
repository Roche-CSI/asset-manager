import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import NotesIcon from '@mui/icons-material/Notes';
import { Tooltip } from "@mui/material";

import style from "./browser.module.scss";

import { Asset, AssetObject } from "../../servers/asset_server";
import { AssetFormatter } from "../../servers/asset_server/formatter";
import { AssetVersion } from "../../servers/asset_server/assetVersion";

import { isEmptyObject, useQuery, useRoute } from "../../utils/utils";
import { convertToCurrentTimeZone } from "../../utils";
import { StoreNames, useStore } from "../../stores";

import VersionSelector from "./VersionSelector";
// import AssetTagsBrowser from "./AssetTagsBrowser"
import { FileTreeViewer } from "../fileTreeViewer";
import { SpinIndicator } from "../spinIndicator";
import { AlertDismissible } from "../alerts";
import ObjectBrowser from "../objectBrowser/ObjectBrowser";

interface AssetBrowserProps {
    asset: Asset;
    className?: string
}

export default function AssetBrowser(props: AssetBrowserProps) {
    const { view } = useParams();

    const query = useQuery();
    const versionNumber = query.get('version');
    const objectId = query.get('object');
    const viewType: string = objectId ? "object" : view as string;

    const route = useRoute();
    const userStore = useStore(StoreNames.userStore, true);
    let className = props.className ? props.className : '';

    // states
    const [activeVersion, setActiveVersion] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const getVersion = (version: any, callback: Function) => {
        if (!version || version.number !== versionNumber || version.asset.id !== props.asset.id) {
            AssetVersion.get(AssetVersion.URL(),
                {
                    asset_id: props.asset.id,
                    user: userStore.get("user").username,
                }).then((data: any) => {
                    props.asset.versions = data.map((o: any) => new AssetVersion(o, props.asset))
                    const newActiveVersion = props.asset.getVersion(versionNumber);
                    AssetVersion.updateVersionObjects(props.asset, newActiveVersion);
                    setActiveVersion((activeVersion: any) => {
                        return newActiveVersion
                    });
                    callback && callback();
                }).catch((error: any) => {
                    setError(error.message)
                })
        } else {
            AssetVersion.updateVersionObjects(props.asset, version);
            setActiveVersion((activeVersion: any) => {
                return version
            });
            callback && callback();
        }
    }

    const getObjects = (version: AssetVersion | null) => {
        if (props.asset.all_objects && !isEmptyObject(props.asset.all_objects)) {
            setLoading(true)
            getVersion(version, () => setLoading(false));
            return;
        }
        // fetch objects and then version
        setLoading(true);
        AssetObject.get(AssetObject.URL(), {
            user: userStore.get("user").username,
            asset_id: props.asset.id
        }
        ).then((data: any) => {
            props.asset.updateObjects(data);
            getVersion(version, () => setLoading(false));
        }).catch((error: any) => {
            setError(error.message)
            setLoading(false);
        })
    }

    useEffect(() => {
        let version: AssetVersion | null = props.asset.getVersion(versionNumber);
        getObjects(version)
    }, [route, props.asset])

    return (
        <div>
            {
                viewType === "object" ? objectBrowser() : assetBrowser()
            }
            {error && <AlertDismissible>{error}</AlertDismissible>}
            {loading &&
                <div className={style.spinnerContainer}>
                    <SpinIndicator message={"Loading..."} />
                </div>
            }
        </div>
    )

    function assetBrowser() {
        return (
            <div>
                {/* <div>
                    <AssetTagsBrowser asset={props.asset}
                                      version={activeVersion}
                                      class_name={class_name}
                                      seq_id={seq_id}
                                      />
                </div> */}
                <div className={style.versionSelector}>
                    <VersionSelector versions={props.asset.versions} activeVersion={activeVersion}
                        asset={props.asset} />
                    {props.asset?.alias &&
                        <Tooltip title={"asset alias"} placement={"right-start"}>
                            <span className={style.alias}>{props.asset.alias}</span>
                        </Tooltip>
                    }
                </div>
                <div>
                    {assetHeader(activeVersion)}
                    {activeVersion && <FileTreeViewer asset={props.asset} activeVersion={activeVersion} />}
                </div>
            </div>
        )
    }

    function assetHeader(version: AssetVersion | null) {
        if (!version) {
            return <div className={style.cardHeader}></div>
        }
        let commit_message = version.commit_message || "first asset commit";
        return (
            <div className={style.cardHeader}>
                <div className={style.infoItems}>
                    <div className={style.headerItem}>
                        <AccountCircleIcon />
                        <span style={{ fontWeight: "bold" }}>{version.created_by}</span>
                        {commit_message && <NotesIcon />}
                        {commit_message && <span>{commit_message}</span>}
                    </div>
                    <div className={style.headerItem}>
                        <span>{version.commit_hash}</span>
                        <AccessTimeIcon />
                        <span>{convertToCurrentTimeZone(version.created_at, "date")}</span>
                    </div>
                </div>
            </div>
        )
    }

    function objectBrowser() {
        return (
            <div>
                {activeVersion && <ObjectBrowser asset={props.asset} objectId={objectId as string} view={viewType} />}
            </div>
        )
    }
}