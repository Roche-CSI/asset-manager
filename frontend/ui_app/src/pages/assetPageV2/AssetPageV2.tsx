import React, { useEffect, useState, useCallback } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Asset } from "../../servers/asset_server";
import { GlobalStore, StoreNames, useStore } from "../../stores";
import { useQuery } from "../../utils/utils";
import { ErrorBoundary } from "../../components/errorBoundary";
import { DefaultAssetView } from "./DefaultAssetView";
import TemplateAssetView from "./TemplateAssetView";
import Switcher from "../../components/assetHistory/Switcher.tsx";
import { CLASS_TYPE } from "../../components/assetClassBrowser";
import { useLoadingState } from "../../components/commonHooks";
import { DataState } from "../../components/commonHooks/useLoadingState";

const DEFAULT_ROOT_VERSION: string = "root";
const DEFAULT_BASE_VERSION: string = "0.0.0";

const VIEWS: string[] = ["files", "history", "graph"];

export const AssetPageV2: React.FC = () => {
	// stores
	const assetStore = useStore(StoreNames.assetStore);
	const recentStore = useStore(StoreNames.recentAssetStore);
	const userStore = useStore(StoreNames.userStore, true);
	const queryStore = useStore(StoreNames.queryStore);
	const classNamesStore = useStore(StoreNames.classNameStore);
	const activeProject = userStore.get("active_project");

	const { loadingState, startFetchingState, completeFetchingState,
		catchFetchingError, fetchingLoader, fetchingError } = useLoadingState();

	const { project_id, class_name, seq_id, view } = useParams();
	const assetClass = classNamesStore.get(class_name as string);
	const project = userStore.get("projects")?.[activeProject] || {}
	// console.log("assetClass:", assetClass);
	// console.log("project:", project);

	const location = useLocation();

	const query = useQuery();
	const version = query.get('version');
	const base = query.get("base") ?? DEFAULT_ROOT_VERSION;
	const compare = query.get("compare") ?? DEFAULT_BASE_VERSION;
	const queryTemplate = query.get("template");
	console.log("location:", location, "template:", queryTemplate);

	const [error, setError] = useState<string>("");
	const [asset, setAsset] = useState<Asset | null>(null);

	if (asset) {
		recentStore.set(
			asset.name(class_name as string),
			{ owner: asset.owner, accessed: new Date().getTime(), url: `${location.pathname}${location.search}` }
		);
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
		const active_project_id: string = userStore.get("active_project");
		if (project_id !== active_project_id) {
			if (Object.keys(userStore.get("projects")).includes(project_id as string)) {
				userStore.set("active_project", project_id);
			} else {
				setError("Oops! You do not have access to the project where this asset is located");
				return;
			}
		}
		let assetName = Asset.getName(class_name as string, seq_id as any);
		let asset = assetStore.get(assetName);
		if (asset) {
			setAsset(asset);
			setParams(asset);
			return;
		}
		startFetchingState();
		Asset.getFromServer(null, assetName, project_id).then((json) => {
			let new_asset = new Asset(json[0]);
			asset = new_asset;
			assetStore.set(assetName, new_asset);
			setAsset(new_asset);
			setParams(asset);
			completeFetchingState()
		}).catch(error => {
			console.log(error);
			catchFetchingError(error.toString())
		});
	}, [class_name, seq_id, project_id, userStore, assetStore]);

	const navigate = useNavigate();
	// Store template value in state
	
	const SwitchComponent: React.FC<{ value: "dashboard" | "default", show?: boolean }> = ({ value, show }) => {
		if (!show) return null;
		return (
			<div className="flex justify-center items-center">
				<Switcher
					size={"sm"}
					value={value}
					options={["dashboard", "default"]}
					setValue={switchAssetView}
				/>
			</div>
		);
	};
	
	const switchAssetView = (view: string) => {
		if (view === "default") {
			const search = new URLSearchParams(location.search);
			search.delete('template');
			navigate(`${location.pathname}?${search.toString()}`);
		}
		if (view === "dashboard") {
			const search = new URLSearchParams(location.search);
			search.delete('template');
			search.set('template', queryTemplate || asset?.attributes.template);
			navigate(`${location.pathname}?${search.toString()}`);
		}
	}
	
	console.log("queryTemplate:", queryTemplate);

	return (
		<div className={`min-h-screen mb-6
			${loadingState.data_state === DataState.fetching && 'flex justify-center items-center'}`}
		>
			<ErrorBoundary>
				{loadingState.data_state === DataState.fetching &&
					<div className="mt-36">
						{fetchingLoader()}
					</div>
				}
				{fetchingError()}
				{
					asset ? queryTemplate ?
						<TemplateAssetView
							templateName={queryTemplate}
							asset={asset}
							switchComponent={<SwitchComponent value={"dashboard"} show={true} />} /> :
						<DefaultAssetView asset={asset}
							setAsset={setAsset}
							projectId={project_id}
							className={class_name}
							view={view}
							switchComponent={
								<SwitchComponent value={"default"}
									show={asset.attributes.template} />
							}
						/>
						: null
				}
			</ErrorBoundary>
		</div>
	);
};
