import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Asset, AssetClass } from "../../servers/asset_server";
import { GlobalStore, useStore, StoreNames } from "../../stores";
import { convertToCurrentTimeZone } from "../../utils";

const PAGE_INDEX: number = 0;
const PAGE_SIZE: number = 10;

export interface AssetSearchTerms {
	owner?: string;
	alias?: string;
	seq_id?: string;
	search_by?: string;
	pageIndex?: number;
	pageSize?: number;
}

export const useAssetList = (assetClass: any) => {
	const assetStore = useStore(StoreNames.assetStore);
	const userStore = useStore(StoreNames.userStore);
	const activeProject: string = userStore.get("active_project");
	
	const [error, setError] = useState<string>('');
	const [pageData, setPageData] = useState<{ data: Asset[], pageCount: number }>({
		data: [],
		pageCount: -1,
	});
	const [progress, setProgress] = useState<{ status: string | null, progress: number }>({ status: null, progress: 0 });
	
	const updateProgress = (received: number, max: number) => {
		setProgress((prev) => ({ ...prev, progress: Math.round((received / max) * 100) }));
	};
	
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
				const defaultAssets: Asset[] = getDefaultAssets(assetStore, assetClass);
				
				if (defaultAssets.length > 0) {
					defaultAssets.sort((a: Asset, b: Asset) => b.seq_id - a.seq_id);
					setPageData({
						data: defaultAssets,
						pageCount: Math.ceil(assetClass.counter / PAGE_SIZE)
					});
					setProgress({ status: "completed", progress: 100 });
					return;
				}
			}
			debugger;
			
			const response: any = await Asset.get(Asset.URL(), {
				class_id: assetClass.id,
				owner,
				alias,
				seq_id,
				page_number: pageIndex + 1,
				page_size: pageSize,
				search_by
			});
			
			const fetchedAssets: Asset[] = response.data.map((data: any) => {
				const asset = new Asset(data);
				assetStore.set(Asset.getName(assetClass.name, asset.seq_id), asset);
				return asset;
			});
			
			setError('');
			setPageData({ data: fetchedAssets, pageCount: response.page_count });
			setProgress({ status: "completed", progress: 100 });
			assetStore.last_update = new Date().getTime();
		} catch (error) {
			console.error('Error fetching assets:', error);
			setError('Error fetching assets from server. Please try again later.');
			setProgress({ status: 'completed', progress: 100 });
		}
	};
	
	const fetchAssetsFromStore = () => {
		let assetList: Asset[] = getDefaultAssets(assetStore, assetClass);
		if (assetList.length === 0) {
			fetchAssetsFromServer({ pageIndex: 0 });
		} else {
			assetList.sort((a: Asset, b: Asset) => b.seq_id - a.seq_id);
			setPageData({ data: assetList, pageCount: Math.ceil(assetClass.counter / PAGE_SIZE) });
			setProgress({ status: "completed", progress: 100 });
		}
	};
	
	useEffect(() => {
		if (assetClass) {
			setProgress({ status: "loading", progress: 0 });
			if (!assetStore.last_update) {
				fetchAssetsFromServer({ pageIndex: 0 });
			} else {
				fetchAssetsFromStore();
			}
		}
	}, [assetClass?.id]);
	
	return {
		pageData,
		error,
		progress
	};
};
