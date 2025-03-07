import React, { useEffect, useState } from "react";
import { StoreNames, useStore } from "../../stores";
import { AssetClass } from "../../servers/asset_server";
import { useLocation, useNavigate } from "react-router-dom";

import { useScrollToRef, useLoadingState } from "../../components/commonHooks";

import {
	ActionsIcon, ExperimentIcon,
	LineageIcon,
	MetadataIcon,
	MonitoringIcon,
	ThreeBarsIcon,
	AddNewIcon
} from "../../components/icons/Icons";
import { isEmptyObject } from "../../utils";
import { FilterBar } from "../../components/filterbar";
import { TabBar } from "../../components/tabbar";
import { DataGrid } from "../../components/datagrid";
import { AssetClassCard, AssetClassCardProps } from "./AssetClassCard";
import { HoveringCodeBlock } from "../../components/hoveringCodeBlock";
import { pythonCode, bashCode } from "./code";
import {
	AlertTriangle,
	BookXIcon, Container, FileCode, FileCode2, FileText, FlaskConical, Image, Layers,
	Lock,
	Menu,
	ShieldAlertIcon,
	Star, Waypoints,
	WaypointsIcon,
	XCircle,
	XCircleIcon
} from "lucide-react";
import { BreadCrumbV2 } from "../../components/breadCrumb/BreadCrumbV2";
import { AccessStatus } from "servers/base/accessStatus.ts";
import { AssetClassCategory, assetClassCategories } from "./assetClassCategories"
import { DataState } from "../../components/commonHooks/useLoadingState";


const ClassListPage: React.FC = () => {
	// store
	const classIdStore = useStore(StoreNames.classIdStore);
	const favoriteClassStore = useStore(StoreNames.favoriteClassStore, true);
	const classNameStore = useStore(StoreNames.classNameStore);
	const userStore = useStore(StoreNames.userStore, true);

	// state
	const [classList, setClassList] = useState<AssetClass[] | null>(null);
	const { loadingState, startFetchingState, completeFetchingState, catchFetchingError, fetchingLoader, fetchingError } = useLoadingState();
	const [projectId, setProjectId] = useState<string>(userStore.get("active_project"))
	const project = userStore.get("projects")?.[projectId];

	// const [allTags, setAllTags] = useState<Tag[]>([]);

	// Calculate deprecated and obsolete counts
	const deprecatedCount = (classList || []).filter((item: AssetClass) =>
		item.status === AccessStatus.DEPRECATED.value
	).length;
	const obsoleteCount = (classList || []).filter((item: AssetClass) =>
		item.status === AccessStatus.OBSOLETE.value
	).length;

	const privateCount = (classList || []).filter((item: AssetClass) =>
		item.status === AccessStatus.PRIVATE.value
	).length;

	const favoriteCount = (classList || []).filter((item: AssetClass) =>
		item.favorite
	).length;

	const linkForTab = (name: string) => `/assets/${name.toLowerCase()}?project_id=${projectId}`

	const TABS = [
		{ name: 'all', icon: <Menu className="size-3.5 mr-2" />, label: "All", link: linkForTab("all") },
		{ name: 'data', icon: <Layers className="size-3 mr-2" />, label: "Datasets", link: linkForTab("data") },
		{ name: 'models', icon: <Waypoints className="size-3.5 mr-2" />, label: "Models", link: linkForTab("models") },
		{
			name: 'containers',
			icon: <Container className="size-3.5 mr-2" />,
			label: "Containers",
			link: linkForTab("containers")
		},
		{
			name: 'configuration',
			icon: <FileCode2 className="size-3.5 mr-2" />,
			label: "Configurations",
			link: linkForTab("configuration")
		},
		{ name: 'images', icon: <Image className="size-3.5 mr-2" />, label: "Images", link: linkForTab("images") },
		{ name: 'reports', icon: <FileText className="size-3.5 mr-2" />, label: "Reports", link: linkForTab("reports") },
		{
			name: 'experimental',
			icon: <FlaskConical className="size-3.5 mr-2" />,
			label: "Experimental",
			link: linkForTab("experimental")
		},
		{
			name: 'favorites',
			icon: <Star className="size-3.5 mr-2" />,
			label: "Favorites",
			link: linkForTab("favorites"),
			floatRight: true,
			bubble: favoriteCount > 0 ? {
				text: favoriteCount.toString(),
				color: "bg-indigo-300 text-indigo-900"
			} : undefined
		},
		{
			name: 'private',
			icon: <Lock className="size-3.5 mr-2" />,
			label: "Private",
			link: linkForTab("private"),
			floatRight: true,
			bubble: privateCount > 0 ? {
				text: privateCount.toString(),
				color: "bg-blue-300 text-primary-900"
			} : undefined
		},

		{
			name: 'deprecated',
			icon: <AlertTriangle className="size-3.5 mr-2" />,
			label: "Deprecated",
			link: linkForTab("deprecated"),
			floatRight: true,
			bubble: deprecatedCount > 0 ? {
				text: deprecatedCount.toString(),
				color: "bg-yellow-300 text-neutral-900"
			} : undefined
		},
		{
			name: 'obsolete',
			icon: <XCircle className="size-3.5 mr-2" />,
			label: "Obsolete",
			link: linkForTab("obsolete"),
			floatRight: true,
			bubble: obsoleteCount > 0 ? {
				text: obsoleteCount.toString(),
				color: "bg-red-400 text-white"
			} : undefined
		},
		// {name: 'alerts', icon: <AlertsIcon className="size-4 mr-1"/> , label: "2", link: "./alerts", accented: true, floatRight: true},
		// {name: 'discussions', icon: <DiscussionsIcon className="size-4 mr-1"/> , label: "10", link: "./discussions", floatRight: true, accented: true},
	];

	const location = useLocation()
	const urlCategory = location.pathname.split("/").pop()
	const activeCategory = assetClassCategories.find((cat: AssetClassCategory) => cat.label.toLowerCase() === urlCategory) || assetClassCategories[0]
	const [classCategories, setClassCategories] = useState<AssetClassCategory[]>(assetClassCategories)
	const [searchTerm, setSearchTerm] = useState<string | null>("")
	// const [category, setCategory] = useState<AssetClassCategory>(defaultCategory)
	const categoryData = classList && activeCategory ? classList.filter((item: AssetClass) => activeCategory.filterFunction(item)) : []
	const renderData = searchTerm
		? categoryData.filter((item: AssetClass) =>
			item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
			item.title.toLowerCase().includes(searchTerm.toLowerCase())
		)
		: categoryData;

	// hooks
	const [classListRef, scrollToClassListRef] = useScrollToRef<HTMLDivElement>();
	const navigate = useNavigate();

	// view
	const VIEWS: string[] = ["", "tags"]
	const view: string = VIEWS[0];

	console.log("activeTab:", activeCategory)

	useEffect(() => {
		// subscribe for login on mount
		const subscription = userStore.subscribe("updates", (data: any) => {
			console.log(
				`"anEvent", was published with updates to userStore`
			);
			const projectId: any = data.active_project || null;
			classIdStore.didFullUpdate = false; //force update class list
			setProjectId(projectId);
		});
		return () => subscription.unsubscribe(); // unsubscribe on unmount
	}, [])

	const addToFavorite = (assetClass: AssetClass) => {
		if (!assetClass) return
		if (assetClass.favorite) {
			favoriteClassStore.remove(assetClass.name)
		} else {
			favoriteClassStore.set(assetClass.name, true)
		}
		//update store
		assetClass.favorite = !assetClass.favorite
		classIdStore.set(assetClass.id, assetClass);
		classNameStore.set(assetClass.name, assetClass);

		const newFavoriteClasses = favoriteClassStore.get()
		const updatedClassList: AssetClass[] = (classList || []).map((item: AssetClass) => {
			item.favorite = newFavoriteClasses?.[item.name]
			return item
		})
		setClassList(updatedClassList);
		// scrollToClassListRef()
	}

	const fetchClassListFromServer = () => {
		let id_map: any = {};
		let name_map: any = {};
		AssetClass.getFromServer(null, null, projectId).then((data: any[]) => {
			const favoriteClasses: any = favoriteClassStore.get()
			data.forEach((o: any, index: number) => {
				let asset_class = new AssetClass(o);
				if (favoriteClasses?.[o.name]) {
					asset_class.favorite = true
				}
				id_map[o.id] = asset_class;
				name_map[o.name] = asset_class;
			})
			classIdStore.set(null, id_map);
			classIdStore.didFullUpdate = true;
			classNameStore.set(null, name_map);
			classNameStore.didFullUpdate = true;
			const list: any = Object.values(classIdStore.get())
			list.sort((item: any, index: number) => (item.favorite ? -1 : 1))
			setClassList((classList: any) => [...list]);
			completeFetchingState()
			console.log(classIdStore.data)
			console.log("classList:", classList);
		}).catch((error: any) => {
			catchFetchingError(error.toString())
		})
	}

	const addFavoriteCategory = () => {
		const favoriteCategory: AssetClassCategory =
			{ idx: 9, class_type: 'favorites', label: 'Favorites', filterFunction: (item: any) => item.favorite }
		const updatedList = [...classCategories];
		updatedList.splice(1, 0, favoriteCategory);
		setClassCategories(updatedList);
	}

	const updateClassList = () => {
		favoriteClassStore.db.getBulkItem(StoreNames.favoriteClassStore)
			.then((favoriteClassesObject: any) => {
				console.log(favoriteClassesObject)
				favoriteClassStore.set(null, favoriteClassesObject)
				if (!isEmptyObject(favoriteClassesObject)) {
					addFavoriteCategory()
				}
				fetchClassListFromServer()
			}).catch((error: any) => {
				console.log(error)
				fetchClassListFromServer()
			})
	}

	useEffect(() => {
		// console.log("ClassListPage - component did mount:", classIdStore.last_update)
		if (!classIdStore.last_update || !classIdStore.didFullUpdate) {
			startFetchingState();
			updateClassList()
		} else {
			const list: any = Object.values(classIdStore.get())
			list.sort((item: any, index: number) => (item.favorite ? -1 : 1))
			setClassList((classList: any) => [...list]);
		}
	}, [projectId]);

	const onCreate = () => {
		// console.log("on create");
		navigate(`/asset_class?action=create&project_id=${projectId}`)
	}

	const Nav = [
		{ name: "projects", url: "/projects", label: "Projects", index: 0 },
		{ name: project.name, url: `/project/${projectId}`, label: project.title || project.name, index: 1 },
		{ name: "assets", url: "", index: 2, label: "Asset Collections" },
	]
	if (activeCategory && activeCategory.label.toLowerCase() !== "all") {
		Nav.push({ name: activeCategory.label.toLowerCase(), url: "", index: 3, label: activeCategory.label })
	}

	const routeGen = (resource: any, id: string) => {
		return `/asset_class?project_id=${projectId}&name=${resource.name}&tab=assets`
	}

	const onSearch = (term: string) => {
		setSearchTerm(term);
	}

	const sortedData = renderData.sort((a: AssetClass, b: AssetClass) => {
		// const aDate = a.modified_date();
		// const bDate = b.modified_date();
		// if (aDate === null || bDate === null) return 0;
		return a.counter < b.counter ? 1 : -1;
	})

	const Card: React.FC<AssetClassCardProps> = ({
		item,
		routeGenerator }) => {
		return (
			<AssetClassCard item={item}
				routeGenerator={routeGenerator}
				isFavorite={item.favorite}
				onFavoriteClicked={addToFavorite} />
		)
	}

	return (
		<div className="mx-auto" ref={classListRef}>
			<div className='bg-base-200 pt-6 px-16'>
				<div className="flex items-center">
					<div className="flex">
						<BreadCrumbV2 items={Nav} />
					</div>
				</div>
				<div className={"pt-6"}>
					<FilterBar
						label={
							<div className="flex items-center space-x-2">
								<p className="text-lg flex items-center">
									{/*<ArtifactsIcon className="size-3 mr-2"/>*/}
									<span>Asset Collections</span>
								</p>
								<p className="text-md text-neutral-500 mr-4">{classList?.length.toLocaleString()}</p>
							</div>}
						onSearch={onSearch}
						placeholder={"Filter by collection name"}
						rightButton={
							<button
								className="btn btn-sm btn-secondary rounded-md"
								onClick={() => onCreate()}>
								<AddNewIcon className="h-3.5 w-3.5 mr-2" />
								<span>New Collection</span>
							</button>
						} />
					<TabBar tabs={TABS} activeTab={activeCategory.label.toLowerCase()} />
				</div>
			</div>
			<div className="mt-6 px-16">
				{loadingState.data_state === DataState.fetching &&
					<div className="mt-32">
						{fetchingLoader()}
					</div>
				}
				{fetchingError()}
				{
					classList &&
					// Add key to DataGrid to force rerender when activeCategory changes
					<DataGrid key={activeCategory.label.toLowerCase()} items={sortedData}
						itemCard={Card}
						routeGenerator={routeGen} cols={4} />
				}
				<HoveringCodeBlock codeVersions={{ python: pythonCode, bash: bashCode }} />
			</div>
		</div>
	)

}

export default ClassListPage;
