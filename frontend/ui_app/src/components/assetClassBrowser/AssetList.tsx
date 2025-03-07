import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined';
import AccessTimeIcon from "@mui/icons-material/AccessTime";

import { Asset, AssetClass } from "../../servers/asset_server";
import { GlobalStore, useStore, StoreNames } from "../../stores";
import { convertToCurrentTimeZone } from "../../utils";

import AssetListControlledTable from "../tables/assetListTable/AssetListControlledTable"
import { AssetSearchTerms } from "../tables/assetListTable/AssetListControlledTable"
import { PageData } from "../tables/controlledPagedTable/controlledReactTable";
import { ProgressBar } from "../progressBars/progressBar";
import { SpinIndicator } from "../spinIndicator";
import { ErrorBoundary } from "../errorBoundary";
import { AlertDismissible } from "../alerts";

import styles from "./browser.module.scss";

interface BrowserProps {
    assetClass: AssetClass;
    className?: string
}

interface AssetResponse {
    data: any[];
    page_count: number;
}

export default function AssetList(props: BrowserProps) {
    const PAGE_INDEX: number = 0;
    const PAGE_SIZE: number = 10;

    const assetStore = useStore(StoreNames.assetStore);
    const userStore = useStore(StoreNames.userStore);
    const active_project: string = userStore.get("active_project")

    const [error, setError] = useState<string>('');
    const [pageData, setPageData] = useState<PageData>({
        data: [],
        pageCount: -1,
    });
    const [progress, setProgress] = useState<any>({ status: null, progress: 0 })

    const updateProgress = (received: number, max: number) => {
        setProgress((progress: any) => { return { ...progress, progress: Math.round((received / max) * 100) } })
    }

    /**
    * Fetch assets from server
    * @param {Object} params - The parameters for fetching assets
    * @param {string} [params.owner=''] - Owner of the asset
    * @param {string} [params.alias=''] - Alias of the asset
    * @param {string} [params.seq_id=''] - Sequence ID of the asset
    * @param {string} [params.search_by=''] - Search criterion
    * @param {number} [params.pageIndex=PAGE_INDEX] - Index of the page to fetch
    * @param {number} [params.pageSize=PAGE_SIZE] - Size of the page to fetch
    * @returns {string} String representation of object {"data": [], "page_count": ""}
    */
    const fetchAssetsFromServer = async ({
        owner = '',
        alias = '',
        seq_id = '',
        search_by = '',
        pageIndex = PAGE_INDEX,
        pageSize = PAGE_SIZE
    }: AssetSearchTerms): Promise<void> => {

        try {
            const shouldFetchDefault = !owner && !alias && !seq_id && !search_by &&
                pageIndex === PAGE_INDEX && assetStore.last_update;

            if (shouldFetchDefault) {
                const defaultAssets: Asset[] = getDefaultAssets(assetStore, props.assetClass);

                if (defaultAssets.length > 0) {
                    defaultAssets.sort((a: Asset, b: Asset) => b.seq_id - a.seq_id);
                    // console.log("assetList:", assetList)
                    setPageData({
                        data: defaultAssets,
                        pageCount: Math.ceil(props.assetClass.counter / PAGE_SIZE)
                    });
                    setProgress({ status: "completed", progress: 100 })
                    return;
                }
            }

            const response: AssetResponse = await Asset.get(Asset.URL(), {
                class_id: props.assetClass.id,
                owner: owner,
                alias: alias,
                seq_id: seq_id,
                page_number: pageIndex + 1,
                page_size: pageSize,
                search_by: search_by
            });

            const fetchedAssets: Asset[] = response.data.map((data: any) => {
                const asset = new Asset(data);
                assetStore.set(Asset.getName(props.assetClass.name, asset.seq_id), asset);
                return asset;
            });
            setError('')
            setPageData({ data: fetchedAssets, pageCount: response.page_count });
            setProgress({ status: "completed", progress: 100 })
            assetStore.last_update = new Date().getTime();
        } catch (error) {
            console.error('Error fetching assets:', error);
            setError('Error fetching assets from server. Please try again later.');
            setProgress({ status: 'completed', progress: 100 });
        }
    };

    const fetchAssetsFromStore = () => {
        let assetList: Asset[] = getDefaultAssets(assetStore, props.assetClass);
        console.log("length: ", assetList.length)
        if (assetList.length === 0) {
            fetchAssetsFromServer({ pageIndex: 0 })
        } else {
            assetList.sort((a: Asset, b: Asset) => b.seq_id - a.seq_id)
            // console.log("assetList:", assetList)
            setPageData({ ...pageData, data: assetList, pageCount: Math.ceil(props.assetClass.counter / PAGE_SIZE) });
            setProgress({ status: "completed", progress: 100 })
        }
    }

    useEffect(() => {
        setProgress({ status: "loading", progress: 0 });
        if (!assetStore.last_update) { // if asset store not yet updated
            fetchAssetsFromServer({ pageIndex: 0 })
        } else { // if yes, get data from asset store
            fetchAssetsFromStore();
        }
    }, [props.assetClass.id])


    if (!props.assetClass) {
        return null;
    }
    console.log("asset_class:", props.assetClass);

    return (
        <ErrorBoundary>
            <div className={`${styles.card}`} style={{border: "2px solid red"}}>
                {
                    progress.status === "loading" &&
                    <div className={styles.progressContainer}>
                        <div className={styles.spinnerContainer}>
                            <SpinIndicator message={"Loading..."} />
                        </div>
                    </div>
                }
                {
                    progress.status !== "loading" &&
                    <div className="flex flex-col justify-between">
                        {/* {header(pageData.data)} */}
                        <AssetListControlledTable
                            pageData={pageData}
                            assetClass={props.assetClass}
                            fetchAssetsFromServer={fetchAssetsFromServer} />
                    </div>
                }
                {error && unknownError(error)}
            </div>
        </ErrorBoundary >
    )


    function header(assetList: Asset[]) {
        const latest = assetList.length > 0 ? assetList[0] : null

        if (!latest) {
            return <div className={styles.cardHeader}></div>
        }
        return (
            <div className={styles.cardHeader}>
                <div className={styles.headerItem}>
                    <AccountCircleIcon />
                    <span style={{ fontWeight: "bold" }}>{latest.created_by}</span>
                    <ArticleOutlinedIcon />
                    <Link to={`/asset/${active_project}/${props.assetClass.name}/${latest.seq_id}/files?version=${latest.leafVersionNumber()}`}>
                        <span>{Asset.getName(props.assetClass.name, latest.seq_id)}</span>
                    </Link>
                    <span>{latest?.alias}</span>
                </div>
                <div className={styles.headerItem}>
                    <span>{latest.owner}</span>
                    <AccessTimeIcon />
                    <span>{convertToCurrentTimeZone(latest.created_at, "date")}</span>
                </div>
            </div>
        )
    }

    /**
     * Get default assets from store
     * @param store Globalstore
     * @param assetClass asset class name
     * @param force boolean
     * @returns a list of assets for the first page, e.g., 1-10
     */
    function getDefaultAssets(store: GlobalStore, assetClass: AssetClass, force: boolean = false) {
        if (force) {
            return [];
        }
        let assets: Asset[] = [];
        let data: any = store.data;
        let latestCount: number = assetClass.counter;
        for (let i: number = latestCount; i >= latestCount - PAGE_SIZE; i--) {
            let assetName = Asset.getName(assetClass.name, i);
            if (data.hasOwnProperty(assetName)) {
                assets.push(new Asset(data[assetName]))
            }
        }
        // Other force refresh criteria: if we have fewer assets than expected.
        if ((latestCount < PAGE_SIZE && assets.length < latestCount) ||
            (latestCount >= PAGE_SIZE && assets.length < PAGE_SIZE)) {
            return [];
        }
        return assets;
    }

    function unknownError(error: string) {
        return (
            <div className={styles.error}>
                <AlertDismissible>
                    {error}
                </AlertDismissible>
            </div>
        )
    }
}
