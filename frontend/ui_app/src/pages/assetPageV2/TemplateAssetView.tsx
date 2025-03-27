import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from "react-router-dom";
import { Maximize2, Minimize2 } from "lucide-react";

import { Asset, AssetObject } from "../../servers/asset_server";
import { BreadCrumbV2 } from "../../components/breadCrumb/BreadCrumbV2";
import { StoreNames, useStore } from "../../stores";
import { toTitleCase, useQuery, isEmptyObject } from "../../utils/utils";
import { AssetVersion } from "../../servers/asset_server/assetVersion";
import { useLoadingState } from "../../components/commonHooks";
import { ParsedObject } from "../../components/objectBrowser/ObjectBrowser";
import { milliSecondsAgo } from "../../utils/dateUtils";
import { DownloadWithProgress } from "../../components/progressBars";
import ComponentContainer from '../../components/componentRegistry/componentContainer';

function parseURL(pathName: string) {
	const pathSegments = pathName.split('/').filter(segment => segment);
	return {
		project_id: pathSegments[1] || null,
		class_name: pathSegments[2] || null,
		seq_id: pathSegments[3] || null,
		view: pathSegments[4] || null,
	};
}

interface Props {
	templateName: string;
	asset: Asset;
	switchComponent: React.ReactNode;
}

const TemplateAssetView: React.FC<Props> = ({ templateName, asset, switchComponent }) => {
	// console.log("asset:", asset);

	const [isFullView, setIsFullView] = useState(false);

	const userStore = useStore(StoreNames.userStore, true);
	const location = useLocation();
	const { project_id, class_name, seq_id, view } = parseURL(location.pathname);
	console.log("project_id:", project_id, "class_name:", class_name, "seq_id:", seq_id, "view:", view);
	const query = useQuery();
	const versionNumber = query.get('version');
	console.log("version:", versionNumber);

	const project = userStore.get("projects")?.[project_id!];
	const projectTitle = project?.title || toTitleCase(project?.name || '');

	const getClassURL = (project_id: string, class_name: string) => {
		return `/asset_class?project_id=${project_id}&name=${class_name}&tab=assets`;
	};

	const Nav = [
		{ name: project?.name, url: `/project/${project_id}`, label: projectTitle, index: 0 },
		{ name: "class_list", url: "/assets", index: 1, label: "Asset Collections" },
		{ name: "class_name", url: getClassURL(project_id!, class_name!), index: 2, label: class_name },
		{ name: "assets", url: ``, label: seq_id, index: 3 },
	];

	const toggleFullView = () => {
		setIsFullView(!isFullView);
	};

	useEffect(() => {
		document.body.style.overflow = isFullView ? 'hidden' : 'unset';
		return () => {
			document.body.style.overflow = 'unset';
		};
	}, [isFullView]);

	const [activeVersion, setActiveVersion] = useState<any>(null);
	const { loadingState, startFetchingState, completeFetchingState,
		catchFetchingError, fetchingLoader, fetchingError } = useLoadingState();
	const signedURLStore = useStore(StoreNames.signedURLStore, true);
	const [contentData, setContentData] = useState<ParsedObject>({});
	const [fileData, setFileData] = useState<any | null>(null);
	const [loading, setLoading] = useState(false);
	const [templateNeedsData, setTemplateNeedsData] = useState<boolean>(asset.attributes?.templateNeedsData || false);

	const SECOND = 1000; //milliseconds
	const MINUTE = 60;
	const limit: number = 60 * SECOND * MINUTE; // 60 mins


	const getVersion = (version: any, callback: Function) => {
		if (!version || version.number !== versionNumber || version.asset.id !== asset.id) {
			AssetVersion.get(AssetVersion.URL(),
				{
					asset_id: asset.id,
					user: userStore.get("user").username,
				}).then((data: any) => {
					asset.versions = data.map((o: any) => new AssetVersion(o, asset))
					const newActiveVersion = asset.getVersion(versionNumber);
					AssetVersion.updateVersionObjects(asset, newActiveVersion);
					setActiveVersion((activeVersion: any) => {
						return newActiveVersion
					});
					callback && callback();
				}).catch((error: any) => {
					catchFetchingError(error.message)
				})
		} else {
			AssetVersion.updateVersionObjects(asset, version);
			setActiveVersion((activeVersion: any) => {
				return version
			});
			callback && callback();
		}
	}

	const getObjects = (version: AssetVersion | null) => {
		if (asset.all_objects && !isEmptyObject(asset.all_objects)) {
			startFetchingState()
			getVersion(version, completeFetchingState);
			return;
		}
		// fetch objects and then version
		startFetchingState()
		AssetObject.get(AssetObject.URL(), {
			user: userStore.get("user").username,
			asset_id: asset.id
		}
		).then((data: any) => {
			asset.updateObjects(data);
			getVersion(version, completeFetchingState);
		}).catch((error: any) => {
			catchFetchingError(error.message)
		})
	}

	useEffect(() => {
		setTemplateNeedsData(asset.attributes?.templateNeedsData || false);
		let version: AssetVersion | null = asset.getVersion(versionNumber);
		getObjects(version)
	}, [asset])

	useEffect(() => {
		if (activeVersion && activeVersion.objects) {
			setLoading(true)
			fetchURL(activeVersion.objects[0]?.id, setContentData) // currently only one file is supported
		}
	}, [activeVersion])

	/**
	 * Fetch signedGCSURL and update in both store and state
	 * @param {string} id Object id
	 * @param setStateCallback function to update state
	 */
	const fetchURL = useCallback((id: string, setStateCallback: Function) => {
		const key: string = `${asset.asset_class}/${id}`;
		signedURLStore.db.getItem(StoreNames.signedURLStore, key)
			.then((existing: any) => {
				const timeElapsed: any = existing && milliSecondsAgo(existing.timestamp);
				if (existing && timeElapsed && timeElapsed <= limit) {
					setStateCallback((contentData: any) => ({
						...contentData,
						...existing
					}));
				} else {
					AssetObject.getSignedGCSURL(asset.asset_class, id).then((data: any) => {
						// console.log("contentData: ", data);
						if (data.error) {
							console.log(data.error)
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
							console.log(message)
						});
				}
			}).catch((error: any) => {
				console.log(error.message)
			})
	}, [])


	const onDownloadComplete = (data: any) => {
		// console.log("download complete", data);
		setFileData(JSON.parse(data));
		setLoading(false);
	}

	const NavBar = () => {
		return (
			<div className="flex justify-between items-center mb-6">
				<BreadCrumbV2 items={Nav} />
				<div className="flex">
					{switchComponent}
					<button
						onClick={toggleFullView}
						className="btn btn-ghost btn-sm">
						{isFullView ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
					</button>
				</div>
			</div>
		)
	}

	const TemplateComponent = () => {
		return (
			<div>
				{templateNeedsData ?
					(fileData &&
						<ComponentContainer
							category={templateName}
							componentProps={{
								fileData: fileData,
								asset: asset,
							}}
						/>)
					:
					(activeVersion &&
						<ComponentContainer
							category={templateName}
							componentProps={{
								asset: {
									...asset,
									activeVersion: activeVersion,
								}
							}}
						/>
					)
				}
			</div>
		)
	}

	return (
		<div className={`${isFullView && 'fixed inset-0 z-50 bg-white flex flex-col'}`}>
			<div className={`${isFullView && 'sticky top-0 bg-white z-10'}`}></div>
			<div className={`${isFullView && 'flex-grow overflow-auto'}`}>
				{contentData && contentData.signedURL && contentData.contentType && loading && templateNeedsData &&
					<DownloadWithProgress url={contentData.signedURL}
						contentType={contentData.contentType}
						onComplete={onDownloadComplete} />
				}
				<div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 bg-base-100">
					<div className="max-w-8xl mx-auto">
						<NavBar />
						<TemplateComponent />
					</div>
				</div>
			</div>
		</div>
	)
};

export default TemplateAssetView;
