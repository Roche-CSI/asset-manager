import React, {useEffect, useState, useCallback} from "react";
import {useLocation, useParams} from "react-router-dom";
import {AssetBrowser, AssetGrapher, AssetHistory} from "../../components";
import {Asset, AssetObject} from "../../servers/asset_server";
import {GlobalStore, StoreNames, useStore} from "../../stores";
import {useQuery} from "../../utils/utils";
import {AlertDismissible} from "../../components/alerts";
import {ErrorBoundary} from "../../components/errorBoundary";
import {BreadCrumbV2} from "../../components/breadCrumb/BreadCrumbV2";
import {ModelCardIcon, ThreeBarsIcon} from "../../components/icons/Icons";
import {TabBar} from "../../components/tabbar";
import AssetBrowserV2 from "./tabs/AssetBrowserV2.tsx";
import {AssetHistoryV2} from "./tabs/AssetHistoryV2.tsx";
import AssetGraphViewV2 from "./tabs/AssetGraphViewV2.tsx";
import {HoveringCodeBlock} from "../../components/hoveringCodeBlock";
import {pythonCode, bashCode} from "./code";
import Spinner from "../../components/spinner/Spinner";
import {Check, Cog, Copy, GitGraph, Info, Layers, Network, Waypoints} from "lucide-react";
import AssetInfoView from "pages/assetPageV2/tabs/AssetInfoView.tsx";
import AssetReadMeView from "pages/assetPageV2/tabs/AssetReadMeView.tsx";
import AssetMetaView from "pages/assetPageV2/tabs/AssetMetaView.tsx";
import ElasticIndexView from "pages/assetClassPageV2/tabs/ElasticIndexView.tsx";


const DEFAULT_ROOT_VERSION: string = "root";
const DEFAULT_BASE_VERSION: string = "0.0.0";

const DEFAULT_VIEW: string = "files";

const VIEWS: string[] = ["files", "history", "graph"];

interface ViewProps {
	asset: Asset;
	setAsset: (asset: Asset) => void;
	projectId: string;
	className?: string;
	view: string;
	switchComponent?: React.ReactNode;
}

const TABS = {
	"files": {label: "Files", icon: <ThreeBarsIcon className="size-3.5 mr-2"/>},
	"info": {label: "About", icon: <Info className="size-3.5 mr-2"/>},
	'readme': {label: "ReadMe", icon: <Layers className="size-3 mr-2"/>},
	"history": {label: "History", icon: <GitGraph className="size-3.5 mr-2"/>},
	"meta": {label: "Metadata", icon: <Waypoints className="size-3.5 mr-2"/>},
	"graph": {label: "Lineage", icon: <Network className="size-3.5 mr-2"/>}
};


const AssetTitle: React.FC<{ asset: Asset; className: string }> = ({ asset, className }) => {
	const [copied, setCopied] = React.useState(false);
	const badgeText = `${className}/${asset?.seq_id}`;
	
	const copyToClipboard = async () => {
		try {
			await navigator.clipboard.writeText(badgeText);
			setCopied(true);
			setTimeout(() => setCopied(false), 2000);
		} catch (err) {
			console.error('Failed to copy text: ', err);
		}
	};
	
	return (
		<div className="flex space-x-8 items-center">
			<h2 className="text-lg text-neutral">
				{asset ? asset.title || asset.name(className) : ""}
			</h2>
			<div className="group flex items-center space-x-2 px-3 py-0.5 text-xs bg-slate-200 text-neutral rounded-full font-medium cursor-pointer">
                <span>
                    {badgeText}
                </span>
				<button
					onClick={copyToClipboard}
					className={`${copied ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} rounded-full transition-all p-0.5`}
					title="Copy to clipboard"
				>
					{copied ? (
						<Check className="size-4 text-neutral" />
					) : (
						<Copy className="size-3 text-neutral-400 hover:text-neutral" />
					)}
				</button>
			</div>
		</div>
	);
};



export const DefaultAssetView: React.FC<ViewProps> = ({
	                                                      asset,
														  setAsset,
	                                                      projectId,
	                                                      className,
	                                                      view,
	                                                      switchComponent
                                                      }) => {
	// stores
	const tab = view || DEFAULT_VIEW;
	const userStore = useStore(StoreNames.userStore, true);
	const queryStore = useStore(StoreNames.queryStore);
	const activeProjectId = userStore.get("active_project");
	const activeProject = userStore.get('projects')?.[activeProjectId] || {};
	const assetClass = useStore(StoreNames.classNameStore).get(className as string);
	const query = useQuery();
	const version = query.get('version');
	const base = query.get("base");
	const compare = query.get("compare");
	
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
					queryStore.set(view, `version=${asset?.leafVersionNumber() || compare}`);
			}
		}, [queryStore]
	);
	
	const setParams = (asset: Asset, base: string = DEFAULT_ROOT_VERSION, compare: string = DEFAULT_BASE_VERSION) => {
		VIEWS.forEach((view: string) => {
			updateQueryStore(view, asset, base, compare);
		});
	};
	
	useEffect(() => {
		view && updateQueryStore(view, asset, base as string, compare as string);
	}, [base, compare, version, view, asset, updateQueryStore]);
	
	useEffect(() => {
		setParams(asset);
	}, [asset]);
	
	const paths = AssetMenu("/asset", projectId, className as string, asset.seq_id, view as string, queryStore);
	
	const Tabs = paths.map((path) => {
		const {label, icon} = TABS[path.label.toLowerCase()];
		return {name: path.label.toLowerCase(), label: label, link: path.route, icon: icon};
	});
	
	const getClassURL = (project_id: string, class_name: string) => {
		return `/asset_class?project_id=${project_id}&name=${class_name}&tab=assets`;
	};
	
	const getViewURL = (class_name: string, seq_id: string, view: string, version: string = DEFAULT_BASE_VERSION) => {
		return `/asset/${userStore.get("active_project")}/${class_name}/${seq_id}/${view}?version=${version}`;
	}
	// console.log("assetClass:", assetClass);
	
	const Nav = [
		{
			name: activeProject.name, url: "/projects",
			label: activeProject.title || activeProject.description, index: 0
		},
		{name: "class_list", url: "/assets", index: 1, label: "Asset Collections"},
		{name: "class_name", url: `${getClassURL(projectId!, className!)}`, index: 2, label: assetClass ? assetClass.title : className},
		{
			name: "seq_id", url: `${getViewURL(className!, asset.seq_id, DEFAULT_VIEW, version)}`,
			index: 3, label: asset.title ? asset.title : asset?.alias ? asset.alias : asset?.seq_id
		},
		{name: "view", url: `${getViewURL(className!, asset.seq_id!, DEFAULT_VIEW, version)}`, index: 4, label: tab}
	];
	
	// console.log("asset:", asset);
	
	return (
		<React.Fragment>
			<div className="bg-base-200 pt-6 px-16">
				<div className="mx-auto">
					<div className="flex flex-col space-y-4">
						<div className="flex justify-between">
                            <BreadCrumbV2 items={Nav}/>
                            {switchComponent}
                        </div>
						<AssetTitle asset={asset} className={className!}/>
						<TabBar tabs={Tabs} activeTab={tab?.toLowerCase()}/>
					</div>
				</div>
			</div>
			<div className="mx-auto px-16">
				{asset && getView(asset, tab)}
			</div>
		</React.Fragment>
	);
	
	function getView(asset: Asset, viewType?: string) {
		switch (viewType) {
			case "info":
				return <AssetInfoView asset={asset} setAsset={setAsset}
				                      assetClassName={className!}/>;
			case "files":
				return <AssetBrowserV2 asset={asset}
				                       className="bg-white border border-gray-200 rounded-lg"/>;
			case "graph":
				return <AssetGraphViewV2 asset={asset}
				                         className="bg-white border border-gray-200 rounded-lg"/>;
			case "history":
				return <AssetHistoryV2 asset={asset}
				                       className="bg-white border border-gray-200 rounded-lg"
				                       view={viewType}/>;
				
			case "readme":
				return <AssetReadMeView asset={asset}/>
			
			case "meta":
				return <AssetMetaView asset={asset}/>
			
			default:
				return null;
		}
	}
	
	function AssetMenu(
		base: string,
		project_id: any,
		className: string,
		seqId: number,
		activeView: string,
		queryStore: GlobalStore
	) {
		const sections = [
			{name: "files", icon: null},
			{name: "info", icon: null},
			{name: "readme", icon: null},
			{name: "history", icon: null},
			{name: "meta", icon: null},
			{name: "graph", icon: null},
			
		];
		return sections.map((section) => ({
			route: `${base}/${project_id}/${className}/${seqId}/${section.name}${queryStore.get(section.name)? `?${queryStore.get(section.name)}`: ''}`,
			label: section.name,
			active: Boolean(section.name === activeView),
			icon: section.icon
		}));
	}
};
