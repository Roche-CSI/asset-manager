import React, { useEffect, useState } from "react";
import { StoreNames, useStore } from "../../stores";
import { Link, useLocation } from "react-router-dom";
import { AssetClass } from "../../servers/asset_server";
import { useQuery } from "../../utils/utils.ts";
import { BreadCrumbV2 } from "../../components/breadCrumb/BreadCrumbV2.tsx";
import { FilterBar } from "../../components/filterbar";
import {PackageX, Ban, Menu, Info, BookText, Image, Dices, FileCog, Cog} from "lucide-react";
import { TabBar } from "../../components/tabbar";
import AssetListView from "pages/assetClassPageV2/tabs/AssetListView.tsx";
import AssetClassView from "pages/assetClassPageV2/tabs/AssetClassView.tsx";
import CLASS_ICONS from "../classListPage/ClassIcons.tsx";
import { Alert } from "../../components/errorBoundary";
import TemplateListView from "pages/assetClassPageV2/tabs/TemplateListView.tsx";
import { ActionsDropdown } from "./ActionsDropDown.tsx";
import ReadMeView from "pages/assetClassPageV2/tabs/ReadMeView.tsx";
import WebhookListView from "pages/assetClassPageV2/tabs/WebhookListView.tsx";
import MetaSchemaView from "pages/assetClassPageV2/tabs/MetaSchemaView.tsx";
import ElasticIndexView from "pages/assetClassPageV2/tabs/ElasticIndexView.tsx";

interface Props {
	project_id: string;
}

export const DisplayAssetClassV2: React.FC<Props> = (props: Props) => {
	const classNameStore = useStore(StoreNames.classNameStore);
	const classIdStore = useStore(StoreNames.classIdStore);
	const userStore = useStore(StoreNames.userStore);
	const assetClassName: string = useQuery().get("name");
	const [assetClass, setAssetClass] = useState<AssetClass | null>(classNameStore.get(assetClassName));
	const [searchTerm, setSearchTerm] = useState<string>("");
	const [error, setError] = useState<string | null>(null);
	
	const location = useLocation();
	const query = useQuery();
	const project_id = query.get("project_id");
	const activeTab = query.get("tab") || "assets";
	const currentProject = userStore.get("projects")?.[project_id];
	const isAdmin: boolean = currentProject?.can_admin_project || false;
	
	
	useEffect(() => {
		const active_project_id: string = userStore.get("active_project");
		console.log("active_project_id:", active_project_id, " props.project_id:", props.project_id);
		if (props.project_id !== active_project_id) {
			if (Object.keys(userStore.get("projects")).includes(props.project_id)) {
				userStore.set("active_project", props.project_id);
			} else {
				setError("Oops! You do not have access to the project where this asset class is located");
				return;
			}
		}
		if (assetClassName) {
			if (!classNameStore.get(assetClassName)) {
				AssetClass.getFromServer(null, assetClassName, userStore.get("active_project")).then((json) => {
					let newClass = new AssetClass(json[0]);
					classNameStore.set(assetClassName, newClass);
					classIdStore.set(newClass.id, newClass); // store by both name and id
					setAssetClass(newClass);
				}).catch((error: any) => {
					console.log(error.message);
					setError("Asset Class Not Found In Current Project");
				});
			} else {
				setAssetClass(classNameStore.get(assetClassName));
			}
		}
	}, [assetClassName, props.project_id, userStore, classNameStore, classIdStore]);
	
	const urlForTab = (tab: string): string => {
		const params = new URLSearchParams(location.search);
		params.set('tab', tab);
		const newSearchParams = params.toString();
		return `${location.pathname}?${newSearchParams}`;
	};
	
	const Nav = [
		{ name: "projects", url: "/projects", label: "Projects", index: 0 },
		{ name: currentProject.name, url: `/project/${project_id}`, label: currentProject.name || currentProject.description, index: 0 },
		{ name: "asset_classes", url: "/assets", index: 1, label: "Asset Collections" },
		{ name: assetClass?.name, url: urlForTab("info"), index: 2, label: assetClass?.title },
		{ name: "artifacts", url: "", index: 3, label: activeTab},
	];
	
	const ACTIONS = [
		{ name: "Obsolete", icon: PackageX },
		{ name: "Deprecate", icon: Ban }
	];
	
	const TABS = [
		{ name: "assets", label: "Assets", icon: <Menu className="size-4 mr-2 text-gray-400" />, link: urlForTab("assets") },
		{ name: "info", label: "About", icon: <Info className="size-4 mr-2 text-gray-400" />, link: urlForTab("info") },
		{ name: "readme", label: "ReadMe", icon: <BookText className="size-3.5 mr-2 text-gray-400" />, link: urlForTab("readme") },
		{ name: "templates", label: "Templates", icon: <Image className="size-3.5 mr-2 text-gray-400" />, link: urlForTab("templates") },
		{ name: "webhooks", label: "Webhooks", icon: <Dices className="size-4 mr-2 text-gray-400" />, link: urlForTab("webhooks") },
		{ name: "meta_schema", label: "Meta Schema", icon: <FileCog className="size-4 mr-2 text-gray-400" />, link: urlForTab("meta_schema") },
		{ name: "elasticsearch", label: "Search Index", icon: <Cog className="size-4 mr-2 text-gray-400" />, link: urlForTab("elasticsearch") },
	];
	
	const Icon = CLASS_ICONS[assetClass?.class_type] || CLASS_ICONS["default"];

	const onSearchEnter = (searchTerm: string) => {
		// console.log("searchTerm:", searchTerm);
		setSearchTerm(searchTerm);
	}
	
	const TabView = ({ tab }) => {
		switch (tab) {
			case "assets":
				return <AssetListView assetClass={assetClass} searchTerm={searchTerm} />;
			case "info":
				return <AssetClassView assetClass={assetClass} setAssetClass={setAssetClass} />;
			case "templates":
				return <TemplateListView assetClass={assetClass} />;
			case "readme":
				return <ReadMeView assetClass={assetClass} />;
			case "webhooks":
				return <WebhookListView assetClass={assetClass}/>;
			
			case "meta_schema":
				return <MetaSchemaView assetClass={assetClass}/>;
			case "elasticsearch":
				return <ElasticIndexView/>
			default:
				return <div>Default</div>;
		}
	};
	
	return (
		<div className="mx-auto">
			<div className="bg-base-200 pt-6 px-16">
				<div className="flex items-center">
					<div className="flex">
						<BreadCrumbV2 items={Nav} />
					</div>
				</div>
				<div className="mt-6">
					<FilterBar
						label={
							<div className="flex items-center space-x-2">
								<p className="text-lg flex items-center">
									{/*<Icon className="size-3 mr-2 text-neutral" />*/}
									{assetClass?.title}
								</p>
								<p className="text-base text-neutral-400 mr-4">
									# Assets: {new Intl.NumberFormat().format(assetClass?.counter || 0)}
								</p>
							</div>
						}
						onKeyPress={onSearchEnter}
						placeholder={"Filter by asset name"}
						// rightButton={<ActionsDropdown actions={ACTIONS} />}
					/>
					<TabBar tabs={TABS} activeTab={activeTab ? activeTab.toLowerCase() : ""} />
				</div>
			</div>
			{assetClass && (
				<div className="px-16 pt-6 flex w-full">
					<TabView tab={activeTab} />
				</div>
			)}
			{error && (
				<div className="pt-6 px-16">
					<Alert variant={"error"} title={"Oh snap! You got an error!"} description={[error]} />
				</div>
			)}
		</div>
	);
};
