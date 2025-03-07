import React, {useEffect, useState} from "react";
import {Link} from "react-router-dom";
import {Asset, AssetClass} from "../../../servers/asset_server";
import {GlobalStore, useStore, StoreNames} from "../../../stores";
import {convertToCurrentTimeZone} from "../../../utils";
import {AssetSearchTerms} from "../../../components/tables/assetListTable/AssetListControlledTable.tsx"
import {PageData} from "../../../components/tables/controlledPagedTable/controlledReactTable.tsx";
import {ErrorBoundary} from "../../../components/errorBoundary";
import {AlertDismissible} from "../../../components/alerts";
import {ControlledDataGrid} from "../../../components/datagrid/ControlledDataGrid.tsx";
import Spinner from "../../../components/spinner/Spinner.tsx";
import AssetCard from "../cards/AssetCard.tsx";
import {Alert} from "../../../components/errorBoundary/Alert.tsx";
import useDidMountEffect from "../../../components/commonHooks/useDidMountEffect.tsx";

interface BrowserProps {
	assetClass: AssetClass;
	searchTerm?: string;
	className?: string
}

interface AssetResponse {
	data: any[];
	page_count: number;
}


export default function AssetListView(props: BrowserProps) {
	const PAGE_NUMBER: number = 1;
	const PAGE_SIZE: number = 10;
	
	const assetStore = useStore(StoreNames.assetStore);
	const userStore = useStore(StoreNames.userStore);
	const active_project: string = userStore.get("active_project")
	
	const [error, setError] = useState<string>('');
	const [pageData, setPageData] = useState<PageData>({
		data: [],
		pageCount: -1,
	});
	
	const [currentPage, setCurrentPage] = useState<number>(PAGE_NUMBER);
	const [rowsPerPage, setRowsPerPage] = useState<number>(PAGE_SIZE);
	
	const [progress, setProgress] = useState<any>({status: null, progress: 0})
	
	const updateProgress = (received: number, max: number) => {
		setProgress((progress: any) => {
			return {...progress, progress: Math.round((received / max) * 100)}
		})
	}
	
	const hasTemplate = props.assetClass.name === "v2_objects";
	
	/**
	 * Fetch assets from server
	 * @param {Object} params - The parameters for fetching assets
	 * @param {string} [params.owner=''] - Owner of the asset
	 * @param {string} [params.alias=''] - Alias of the asset
	 * @param {string} [params.seq_id=''] - Sequence ID of the asset
	 * @param {string} [params.search_by=''] - Search criterion
	 * @param {number} [params.pageNumber=PAGE_NUMBER] - page number to fetch, start from 1
	 * @param {number} [params.pageSize=PAGE_SIZE] - Size of the page to fetch
	 * @returns {string} String representation of object {"data": [], "page_count": ""}
	 */
	const fetchAssetsFromServer = async ({
		                                     owner = '',
		                                     alias = '',
		                                     seq_id = '',
		                                     search_by = '',
		                                     pageNumber = PAGE_NUMBER,
		                                     pageSize = PAGE_SIZE
	                                     }: AssetSearchTerms): Promise<void> => {
		
		try {
			setProgress({status: "loading", progress: 0});
			const shouldFetchDefault = !owner && !alias && !seq_id && !search_by &&
				pageNumber === PAGE_NUMBER && pageSize === PAGE_SIZE && assetStore.last_update;
			
			if (shouldFetchDefault) {
				const defaultAssets: Asset[] = getDefaultAssets(assetStore, props.assetClass);
				
				if (defaultAssets.length > 0) {
					defaultAssets.sort((a: Asset, b: Asset) => b.seq_id - a.seq_id);
					// console.log("assetList:", assetList)
					setPageData({
						data: defaultAssets,
						pageCount: Math.ceil(props.assetClass.counter / PAGE_SIZE)
					});
					setProgress({status: "completed", progress: 100})
					return;
				}
			}
			
			const response: AssetResponse = await Asset.get(Asset.URL(), {
				class_id: props.assetClass.id,
				owner: owner,
				alias: alias,
				seq_id: seq_id,
				page_number: pageNumber,
				page_size: pageSize,
				search_by: search_by
			});
			
			const fetchedAssets: Asset[] = response.data.map((data: any) => {
				const asset = new Asset(data);
				assetStore.set(Asset.getName(props.assetClass.name, asset.seq_id), asset);
				return asset;
			});
			setError('')
			setPageData({data: fetchedAssets, pageCount: response.page_count});
			setProgress({status: "completed", progress: 100})
			assetStore.last_update = new Date().getTime();
		} catch (error) {
			console.error('Error fetching assets:', error);
			setError('Error fetching assets from server. Please try again later.');
			setProgress({status: 'completed', progress: 100});
		}
	};
	
	const fetchAssetsFromStore = () => {
		let assetList: Asset[] = getDefaultAssets(assetStore, props.assetClass);
		// console.log("length: ", assetList.length)
		if (assetList.length === 0) {
			fetchAssetsFromServer({pageNumber: 1})
		} else {
			setProgress({status: "loading", progress: 0});
			assetList.sort((a: Asset, b: Asset) => b.seq_id - a.seq_id)
			// console.log("assetList:", assetList)
			setPageData({ data: assetList, pageCount: Math.ceil(props.assetClass.counter / PAGE_SIZE)});
			setProgress({status: "completed", progress: 100})
		}
	}
	
	useEffect(() => {
		if (!assetStore.last_update) { // if asset store not yet updated
			fetchAssetsFromServer({pageNumber: 1, pageSize: rowsPerPage})
		} else { // if yes, get data from asset store
			fetchAssetsFromStore();
		}
	}, [props.assetClass.id])

	useEffect(() => {
		fetchAssetsFromServer({pageNumber: 1, search_by: props.searchTerm, pageSize: rowsPerPage})
    }, [props.searchTerm])
	
	if (!props.assetClass) {
		return null;
	}
	
	// filter if title, description, seq_id, alias, username etc. matches the search term
	// const renderData = props.searchTerm ? pageData.data.filter((asset: Asset) => asset.matchesSearch(props.searchTerm)) : pageData.data
	
    pageData.data.forEach((asset: Asset) => {
	    const query = hasTemplate ? `version=${asset.leafVersionNumber()}&template=true` : `version=${asset.leafVersionNumber()}`;
        asset.identifier = asset.title ? asset.title : asset.alias ? asset.alias : asset.name(props.assetClass.name);
	    asset.link = `/asset/${active_project}/${props.assetClass.name}/${asset.seq_id}/files?${query}`;
		asset.description = asset.description ? asset.description : "No description available";
    });

	const onPageChange = (page: number, rowsPerPage: number) => {
		setCurrentPage(page)
		fetchAssetsFromServer({pageNumber: page, search_by: props.searchTerm, pageSize: rowsPerPage})
	}

	const onRowsPerPageChange = (rowsPerPage: number) => {
		setRowsPerPage(rowsPerPage)
		fetchAssetsFromServer({pageNumber: 1, pageSize: rowsPerPage})
	}
	console.log("pageData:", pageData);
	
	const Card: React.FC<{ item: any }> = ({ item }) => (
		<AssetCard item={item} className={props.assetClass.name}/>
	)
	
	return (
		<ErrorBoundary>
			<div className="w-full">
				{
					progress.status === "loading" &&
					<div className='mt-32'><Spinner message={"Loading"}/></div>
				}
                {
                    progress.status !== "loading" &&
                    <div>
                        <div className="text-lg text-neutral mb-6 font-semibold">{`List of Assets`}</div>
                        <ControlledDataGrid cols={3}
                                            items={pageData.data}
                                            itemCard={Card}
                                            numOfPages={pageData.pageCount}
                                            length={props.searchTerm? (pageData.pageCount * rowsPerPage): props.assetClass.counter}
                                            currentPage={currentPage}
                                            rowsPerPage={rowsPerPage}
                                            onPageChange={onPageChange}
                                            onRowsPerPageChange={onRowsPerPageChange}
                                            selfPagination={false}/>
                    </div>
                }
				{error && unknownError(error)}
			</div>
		</ErrorBoundary>
	)
	
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
		for (let i: number = latestCount; i > latestCount - PAGE_SIZE; i--) {
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
			<Alert variant={"error"} title={"Oh snap! You got an error!"} description={[error]}/>
		)
	}
}
