import React, { useEffect, useState, useCallback } from "react";
import { useLocation, useParams } from "react-router-dom";
import styles from "./asset_page.module.scss";
import { AssetBrowser, AssetGrapher, AssetHistory } from "../../components";
import { Asset, AssetObject } from "../../servers/asset_server";
import { GlobalStore, StoreNames, useStore } from "../../stores";
import { useQuery } from "../../utils/utils";
import { AlertDismissible } from "../../components/alerts";
import { ErrorBoundary } from "../../components/errorBoundary";
import { CopyButton } from "../../components/copyButton";
import Breadcrumb, { BreadcrumbItem } from "../../components/breadCrumb/Breadcrumb";
import MenuTab from "../../components/menuTab/MenuTab";

export const CodeBlockIcon = ({ className }: { className: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg"
        fill="none" viewBox="0 0 24 24"
        strokeWidth={1.5} stroke="currentColor"
        className={className}>
        <path strokeLinecap="round"
            strokeLinejoin="round"
            d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
        />
    </svg>
)

interface InfoTooltipProps {
    codeSample: string;
    infoIconClassName?: string;
    tooltipClassName?: string;
}

const InfoTooltip: React.FC<InfoTooltipProps> = ({ codeSample, infoIconClassName = "", tooltipClassName = "" }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div className="relative flex items-center"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}>
            <span className={`cursor-pointer ${infoIconClassName}`}>
                <CodeBlockIcon className={"h-6 w-6 text-gray-700 hover:text-blue-500"} />
            </span>
            {isHovered && (
                <div className={`absolute top-full left-1/2 transform -translate-x-1/2 p-2 z-10`}
                    style={{ width: 'auto' }}
                >
                    <div className={`bg-gray-800 rounded-md ${tooltipClassName}`}>
                        <CodeBlock codeString={codeSample} />
                        <button
                            className="absolute top-4 right-4 bg-blue-500 text-white text-xs px-2 py-1 rounded-md focus:outline-none"
                            onClick={() => {
                                navigator.clipboard.writeText(codeSample);
                                alert('Code copied to clipboard');
                            }}
                        >
                            Copy
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

const CodeBlock = ({ codeString }: { codeString: string }) => {
    return (
        <div className="mockup-code !text-yellow-500 w-max">
            <pre data-prefix="$"><code>{codeString}</code></pre>
        </div>
    );
};


const DEFAULT_ROOT_VERSION: string = "root";
const DEFAULT_BASE_VERSION: string = "0.0.0";

const VIEWS: string[] = ["files", "history", "graph"];

export default function AssetPage() {
    // stores
    const assetStore = useStore(StoreNames.assetStore);
    const recentStore = useStore(StoreNames.recentAssetStore);
    const userStore = useStore(StoreNames.userStore, true);
    // store the query params in a separate store so that the menu bar click can navigate back to there
    const queryStore = useStore(StoreNames.queryStore)

    const { project_id, class_name, seq_id, view } = useParams();
    const location = useLocation()

    const query = useQuery();
    const version = query.get('version');
    const objectId = query.get('object');
    const base = query.get("base");
    const compare = query.get("compare");
    console.log("query:", query, "version:", version, "objectId:", objectId);
    // console.log("query-string:", qs.parse(useLocation().search));

    const [error, setError] = useState<string>("")
    const [asset, setAsset] = useState<Asset | null>(null);

    if (asset) {
        recentStore.set(
            asset.name(class_name as string),
            { owner: asset.owner, accessed: new Date().getTime(), url: `${location.pathname}${location.search}` })
    }

    const updateQueryStore = useCallback(
        (view: string, asset: Asset | null, base: string = DEFAULT_ROOT_VERSION, compare: string = DEFAULT_BASE_VERSION) => {
            switch (view) {
                case "history":
                    queryStore.set(view, `base=${base}&compare=${compare}`);
                    break;
                case "graph":
                    queryStore.set(view, `version=${compare}`);
                    break;
                default:
                    queryStore.set(view, `version=${asset?.leafVersionNumber() || compare}`)
            }
        }, [queryStore])

    const setParams = (asset: Asset, base: string = DEFAULT_ROOT_VERSION, compare: string = DEFAULT_BASE_VERSION) => {
        VIEWS.forEach((view: string, index: number) => {
            updateQueryStore(view, asset, base, compare)
        })
    }

    useEffect(() => {
        view && updateQueryStore(view, asset, base as string, compare as string)
    }, [base, compare, version, view])

    useEffect(() => {
        /***
         * user could directly copy & paste the asset-url in browser, in which case the
         * store may not have the asset data. we check and load from asset_server if required.
         */
        const active_project_id: string = userStore.get("active_project");
        console.log("active_project_id:", active_project_id, " project_id:", project_id)
        if (project_id !== active_project_id) {
            if (Object.keys(userStore.get("projects")).includes(project_id as string)) {
                userStore.set("active_project", project_id);
            } else {
                setError("Oops! You do not have access to the project where this asset is located");
                return
            }
        }
        let assetName = Asset.getName(class_name as string, seq_id as any);
        let asset = assetStore.get(assetName);
        setParams(asset) // set default query params
        Asset.getFromServer(null, assetName, project_id).then((json) => {
            let new_asset = new Asset(json[0]);
            asset = new_asset
            assetStore.set(assetName, new_asset);
            setAsset(new_asset);
            setParams(asset)
        }).catch(error => {
            console.log(error);
        })
    }, [class_name, seq_id])

    // console.log("recents:", recentStore.data);
    const paths = AssetMenu("/asset", project_id, class_name as string, seq_id as any, view as string, queryStore)

    return (
        <div className='p-4'>
            {header()}
            {
                <MenuTab paths={paths}>
                    <ErrorBoundary>
                        {asset && getView(asset, view)}
                    </ErrorBoundary>
                </MenuTab>
            }
            {error && <AlertDismissible>{error}</AlertDismissible>}
        </div>
    )

    function getView(asset: Asset, viewType?: string) {
        switch (viewType) {
            case "files":
                return <AssetBrowser asset={asset} className={styles.card} />
            case "graph":
                return <AssetGrapher asset={asset} className={styles.card} />
            case "history":
                return <AssetHistory asset={asset} className={styles.card} view={viewType} />
            default:
                return null
        }
    }

    function headerItems(
        class_name: string,
        seq_id: number,
        view: string,
        version?: string,
        objectId?: string,
        base?: string,
        compare?: string
    ) {
        const classURL = `/asset_class?project_id=${userStore.get("active_project")}&name=${class_name}`;
        const assetURL = `/asset/${userStore.get("active_project")}/${class_name}/${seq_id}/files?version=${version || "0.0.0"}`
        const viewURL = `/asset/${userStore.get("active_project")}/${class_name}/${seq_id}/${view}`
        const versionURL = version ? `${viewURL}?version=${version}` : null
        const objectURL = version && objectId ? `${versionURL}?object=${objectId}` : null;
        const fileName = objectId ? AssetObject.parseId(objectId)[1] : null;
        const historyURL = base ? `${viewURL}?base=${base}&compare=${compare}` : null;

        const items: BreadcrumbItem[] = [
            { index: 0, name: "assets", url: "/assets" },
            { index: 1, name: class_name, url: classURL },
            { index: 2, name: seq_id.toString(), url: assetURL },
        ]
        let title: string = "";
        if (version && versionURL) {
            title = `${class_name}/${seq_id}/${version || "0.0.0"}`;
            items.push({ index: 3, name: version.toString(), url: versionURL })
        }
        if (fileName && objectURL) {
            const fileNames: string[] = fileName.split("/");
            title = fileNames[fileNames.length - 1]
            items.push({ index: 3, name: fileName.toString(), url: objectURL })
        }
        if (historyURL) {
            title = `base=${base}&compare=${compare}`;
            items.push({ index: 3, name: `base=${base}&compare=${compare}`, url: historyURL })
        }
        // console.log("items:", items);
        let children: any;
        if (view === "files") {
            children = <InfoTooltip
                codeSample={`asset clone ${class_name}/${seq_id}/${version || "0.0.0"}`}
                infoIconClassName="text-gray-600 hover:text-blue-500"
            />
            // children = <CopyButton
            //     textToCopy={`${class_name}/${seq_id}/${version || "0.0.0"}`}
            //     tooltip={"copy asset name"}
            // />
        }
        return { items, children, title }
    }

    function header() {
        const { items, children, title } = headerItems(
            class_name as string,
            seq_id as any,
            view as string,
            version as any, // any here because its nullable
            objectId as any,
            base as any,
            compare as any
        )
        return (
            <Breadcrumb items={items} children={children} title={title} />
        )
    }

    function AssetMenu(base: string,
        project_id: any,
        className: string,
        seqId: number,
        activeView: string,
        queryStore: GlobalStore
    ) {
        const sections = [
            { name: "files", icon: null }, //DocumentScannerOutlined
            { name: "history", icon: null }, //HistoryOutlined
            { name: "graph", icon: null } //AccountTreeOutlined
        ]
        const paths = sections.map((section, index) => {
            return {
                route: `${base}/${project_id}/${className}/${seqId}/${section.name}?${queryStore.get(section.name)}`,
                label: section.name,
                active: Boolean(section.name === activeView),
                icon: section.icon
            }
        })
        return paths
    }
}