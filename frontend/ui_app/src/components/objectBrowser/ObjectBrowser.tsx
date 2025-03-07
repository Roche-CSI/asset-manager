import React, {useCallback, useEffect, useState} from "react";
import {Asset, AssetObject} from "../../servers/asset_server";
import {StoreNames, useStore} from "../../stores";
import {FileViewer} from "../fileViewer";
import FileDiffViewer from "../../components/fileViewer/FileDiffViewer";
import {SpinIndicator} from "../spinIndicator";
import { ErrorBoundary } from "../errorBoundary";
import { milliSecondsAgo} from "../../utils/dateUtils";
import { normalizeQueryParam } from "../../utils/utils";
import { diffItem, diffObject } from "../../servers/asset_server/assetVersion"
import defaultStyles from "./browser.module.scss";

interface BrowserProps {
    asset: Asset;
    objectId?: string;
    path?: string;
    className?: string;
    view: string;
    diffObject?: diffObject;
    base?: string;
    compare?: string;
    header?: boolean;
}

export interface ParsedObject {
    signedURL?: string;
    contentType?: string;
    fileName?: string;
    objectData?: any;
    timestamp?: number;
}

const SECOND = 1000; //milliseconds
const MINUTE = 60;
const limit: number = 60 * SECOND * MINUTE; // 60 mins

export default function ObjectBrowser(props: BrowserProps) {
    const signedURLStore = useStore(StoreNames.signedURLStore, true);
    const [contentData, setContentData] = useState<ParsedObject>({});
    const [prevData, setPrevData] = useState<ParsedObject>({});
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const objectId: string = normalizeQueryParam(props.objectId) ?? "";

    /**
    * Fetch signedGCSURL and update in both store and state
    * @param {string} id Object id
    * @param setStateCallback function to update state
    */
    const fetchURL = useCallback((id: string, setStateCallback: Function) => {
        const key: string = `${props.asset.asset_class}/${id}`;
        setLoading(true);
        signedURLStore.db.getItem(StoreNames.signedURLStore, key)
            .then((existing: any) => {
                const timeElapsed: any = existing && milliSecondsAgo(existing.timestamp);
                if (existing && timeElapsed && timeElapsed <= limit) {
                    setStateCallback((contentData: any) => ({
                        ...contentData,
                        ...existing
                    }));
                } else {
                    AssetObject.getSignedGCSURL(props.asset.asset_class, id).then((data: any) => {
                        // console.log("contentData: ", data);
                        if (data.error) {
                            setError(data.error)
                            return
                        }
                        let parsed: ParsedObject = {
                            signedURL: data.signed_url,
                            contentType: AssetObject.getContentType(id, data.object.content.mime_type),
                            fileName: AssetObject.parseId(id)[1],
                            objectData: data.object,
                            timestamp: new Date().getTime(),
                        };
                        signedURLStore.set(key, parsed);
                        setStateCallback((contentData: any) => ({
                            ...contentData,
                            ...parsed
                        }));
                    })
                    .catch((error: any) => {
                        const message: string =
                            `Snap! There was an error fetching this file. This file may not exist.
                            Please try again later.
                            `;
                        setError(message)
                    });
                }
            }).catch((error: any) => {
                setError(error.message)
            }).finally(() => {
                setLoading(false)
            })
    },[props.asset, signedURLStore])

    useEffect(() => {
        if (objectId) { // single file view
            fetchURL(objectId, setContentData)
        }
        else if (props.path && props.diffObject) {
            let diffItem: diffItem = props.diffObject[props.path];
            // console.log("diff: ", diff)
            if (!diffItem) { // if root === compare
                return;
            }
            if (diffItem.prevId) { //object was altered/removed in current version
                fetchURL(diffItem.prevId, setPrevData)
                if (diffItem.id) { // altered
                    fetchURL(diffItem.id, setContentData)
                } else { //removed
                    setContentData({})
                }
            } else if (diffItem.id) { //object was added in current version
                setPrevData({})
                fetchURL(diffItem.id, setContentData)
            }
        }
    }, [props.path, fetchURL, props.view, props.asset, props.diffObject])

    const data: any = contentData as any;
    const styles: any = props.className?? defaultStyles;
    const header: boolean = typeof props.header !== "undefined"? props.header: true;

    return (
        <div className="">
            <ErrorBoundary>
                {props.view === "object" ?
                <FileViewer
                    header={header}
                    url={data.signedURL}
                    contentType={data.contentType}
                    fileName={data.fileName}
                    objectData={data.objectData}
                    error={error}
                    asset={props.asset}
                />
                :
                <FileDiffViewer
                    url={contentData.signedURL}
                    contentType={contentData.contentType || prevData.contentType}
                    fileName={contentData.fileName || prevData.fileName}
                    objectData={contentData.objectData}
                    prevURL={prevData.signedURL}
                    prevObjectData={prevData.objectData}
                    base={props.base}
                    compare={props.compare}
                    error={error}
                />
                }
                {loading && <SpinIndicator message={"loading"}
                                           className={styles.spinner} />}
            </ErrorBoundary>
        </div>
    )
}
