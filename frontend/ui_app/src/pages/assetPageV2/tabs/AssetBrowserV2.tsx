import React, { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Calendar, GitCommit, ReceiptText, UserCircle } from "lucide-react";

import { Asset, AssetObject } from "../../../servers/asset_server";
import { AssetVersion } from "../../../servers/asset_server/assetVersion";

import { isEmptyObject, normalizeQueryParam, useQuery, useRoute } from "../../../utils/utils";
import { convertToCurrentTimeZone } from "../../../utils";
import { StoreNames, useStore } from "../../../stores";

import VersionSelector from "../../../components/assetBrowser/VersionSelector";
// import AssetTagsBrowser from "./AssetTagsBrowser"
import { FileTreeViewer } from "../../../components/fileTreeViewer";
import ObjectBrowser from "../../../components/objectBrowser/ObjectBrowser";
import FileBreadCrumb from "../../../components/fileViewer/FileBreadCrumb";
import { useLoadingState } from "../../../components/commonHooks";
import { DataState } from "../../../components/commonHooks/useLoadingState";

interface AssetBrowserProps {
    asset: Asset;
    className?: string
}

const AssetBrowserV2: React.FC<AssetBrowserProps> = (props) => {
    const { view } = useParams();

    const query = useQuery();
    const location = useLocation();
    const navigate = useNavigate();
    const versionNumber = query.get('version');
    const objectId = normalizeQueryParam(query.get('object'));
    const viewType: string = objectId ? "object" : view as string;
    const folderId = normalizeQueryParam(useQuery().get("folder"));

    const route = useRoute();
    const userStore = useStore(StoreNames.userStore, true);
    let className = props.className ? props.className : '';

    // states
    const [activeVersion, setActiveVersion] = useState<any>(null);
    const { loadingState, startFetchingState, completeFetchingState,
        catchFetchingError, fetchingLoader, fetchingError } = useLoadingState();

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
                    catchFetchingError(error.message)
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
            startFetchingState()
            getVersion(version, completeFetchingState);
            return;
        }
        // fetch objects and then version
        startFetchingState()
        AssetObject.get(AssetObject.URL(), {
            user: userStore.get("user").username,
            asset_id: props.asset.id
        }
        ).then((data: any) => {
            props.asset.updateObjects(data);
            getVersion(version, completeFetchingState);
        }).catch((error: any) => {
            catchFetchingError(error.message)
        })
    }

    useEffect(() => {
        let version: AssetVersion | null = props.asset.getVersion(versionNumber);
        getObjects(version)
    }, [route, props.asset])

    const path = objectId ? objectId.split("==::")[1] : folderId
    console.log("path: ", path)

    const navigateToFolder = (path: string) => {
        let target = `${location.pathname}?version=${versionNumber}`;
        if (path) {
            target += `&folder=${path}`
        }
        navigate(target);
    }

    return (
        <div>
            <div className={`${loadingState.data_state === DataState.fetching && 'mt-4'}`}>
                {fetchingLoader()}
            </div>
            {fetchingError()}
            {activeVersion &&
                <div>
                    <div className="my-4 flex space-x-8 items-center">
                        <VersionSelector versions={props.asset.versions} activeVersion={activeVersion}
                            asset={props.asset} />
                        <FileBreadCrumb path={path} onClick={navigateToFolder} separator={"/"} />
                    </div>
                    {
                        viewType === "object" ? objectBrowser() : assetBrowser()
                    }
                </div>
            }
        </div>
    )

    function assetBrowser() {
        return (
            <div className="">
                {/* <div>
                    <AssetTagsBrowser asset={props.asset}
                                      version={activeVersion}
                                      class_name={class_name}
                                      seq_id={seq_id}
                                      />
                </div> */}
                <div className="">
                    {assetHeader(activeVersion)}
                    <FileTreeViewer asset={props.asset} activeVersion={activeVersion} />
                </div>
            </div>
        )
    }

    function assetHeader(version: AssetVersion | null) {
        if (!version) {
            return <div className=''></div>
        }
        let commit_message = version.commit_message || "first asset commit";
        return (
            <div className="h-[65px] p-4 border border-base-300 border-b-0 bg-base-100 rounded-t-lg flex justify-between text-neutral-600">
                <div className="flex justify-between w-full">
                    <div className="flex items-center text-xs space-x-6">
                        <span className="flex space-x-2">
                            <UserCircle className="size-4" />
                            <span className="">{version.created_by}</span>
                        </span>
                        <span className="flex space-x-2">
                            {commit_message && <ReceiptText className="size-4" />}
                            {commit_message && <span className="mr-4">{commit_message}</span>}
                        </span>
                    </div>
                    <div className="flex items-center text-xs space-x-6">
                        <span className="flex space-x-2">
                            <GitCommit className="size-4" />
                            <span className="">{version.commit_hash}</span>
                        </span>
                        <span className="flex space-x-2">
                            <Calendar className="size-4" />
                            <span>{convertToCurrentTimeZone(version.created_at, "date")}</span>
                        </span>
                    </div>
                </div>
            </div>
        )
    }

    function objectBrowser() {
        return (
            <div className="">
                <ObjectBrowser asset={props.asset} objectId={objectId as string} view={viewType} />
            </div>
        )
    }
}

export default AssetBrowserV2;
