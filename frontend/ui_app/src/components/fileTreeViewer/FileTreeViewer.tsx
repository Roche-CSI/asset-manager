import {
    ChonkyActions,
    ChonkyFileActionData,
    defineFileAction,
    reduxActions,
    FileArray,
    FileBrowser,
    FileContextMenu,
    FileData,
    FileHelper,
    FileList,
    FileToolbar,
} from 'chonky';
import React, {useCallback, useEffect, useMemo, useState, useRef} from 'react';
import DemoFsMap from './data.json';
import styles from "./tree.module.scss";
import {Asset, AssetObject} from "../../servers/asset_server";
import {useLocation, useNavigate, useParams, Navigate} from "react-router-dom";
import {isEmptyObject, useQuery, normalizeQueryParam} from "../../utils/utils";
import {AssetVersion} from "../../servers/asset_server/assetVersion";
import ObjectTree from "../../servers/asset_server/objectTree";
import Content from "../../servers/asset_server/content";
import {StoreNames, useStore} from "../../stores";
import {ObjectBrowser} from '../objectBrowser';
import {FileIcon} from './FileIcon';
// import { FileTree } from '../../utils';

// global chonky settings - will affect all chonky instances
// setChonkyDefaults({iconComponent: FileIcon});

const rootFolderId = DemoFsMap.rootFolderId;
const fileMap = (map: any) => {
	return (map.fileMap as unknown) as {
		[fileId: string]: FileData & { childrenIds: string[] };
	};
}

export const useFiles = (currentFolderId: string, map: any): FileArray => {
	return useMemo(() => {
		const currentFolder = (map && !isEmptyObject(map)) ? map[currentFolderId] : null;
		const files = currentFolder && currentFolder.childrenIds
			? currentFolder.childrenIds.map((fileId: string) => map[fileId] ?? null)
			: [];
		return files;
	}, [currentFolderId, map]);
};

export const useFolderChain = (currentFolderId: string, map: any): FileArray => {
	return useMemo(() => {
		const currentFolder = map[currentFolderId];
		const folderChain = [currentFolder];
		let parentId = currentFolder ? currentFolder.parentId : null;
		while (parentId) {
			const parentFile = map[parentId];
			if (parentFile) {
				folderChain.unshift(parentFile);
				parentId = parentFile.parentId;
			} else {
				parentId = null;
			}
		}
		return folderChain;
	}, [currentFolderId]);
};

/**
 * Returns an array of content ids for files only inside the current folder
 */
export const getCurrentIds = (folderTree: any, setReadmeObjectId: Function, folderId?: string): any[] => {
	let contentIds: any[] = [];
	let fileMap: any = folderTree.fileMap;
	let readmeObjectId: string = ''
	if (!folderId || (folderId === folderTree.rootFolderId)) { //root folder
		for (let x in fileMap) {
			if (!x.includes("/") && fileMap[x].isFile) {
				contentIds.push(fileMap[x].content_id)
				// If this file is a readme file
				if (x.toLowerCase().includes("readme")) {
					readmeObjectId = fileMap[x].object_id
				}
			}
		}
	} else { //nested folder
		let children: any[] = fileMap[folderId].children;
		children.forEach((x: any) => {
			// If this file is a readme file
			if (x.isFile && x.name.toLowerCase().includes("readme")) {
				readmeObjectId = x.object_id
			}
			return x.isFile && contentIds.push(x.content_id)
		})
	}
	setReadmeObjectId(readmeObjectId)
	return contentIds
}

interface contentObjects {
	[key: string]: {};
}

interface FileViewerProps {
	asset: Asset;
	activeVersion: AssetVersion | null;
	loading?: boolean;
}


export const FileTreeViewer: React.FC<FileViewerProps> = (props) => {
	const [currentFolderId, setCurrentFolderId] = useState(rootFolderId);
	const [fileTree, setFileTree] = useState<any>(null);
	const {class_name, seq_id, view} = useParams();
	const [assetName, setAssetName] = useState<string | null>(`${class_name}/${seq_id}`);
	const location = useLocation()
	const navigate = useNavigate();
	const version_number = useQuery().get("version");
	const baseURL = `${location.pathname}${location.search}`;
	const folder_id = normalizeQueryParam(useQuery().get("folder"));
	const userStore = useStore(StoreNames.userStore, true);
	const contentStore = useStore(StoreNames.contentStore);
	const [readmeObjectId, setReadmeObjectId] = useState<string>('');
	const toolbarRef = useRef<any>(null);
	
	/**
	 * Returns stored contents using content ids
	 * @param content_ids Array of content ids
	 * @return a pair of values: stored content objects and ids not in store
	 */
	const getStoredContents = (content_ids: any[]): any[] => {
		let storedContentObject: contentObjects = {};
		let updatedContentIds: string[] = [];
		content_ids.forEach((id: string) => {
			if (contentStore.get(id)) {
				storedContentObject[id] = contentStore.get(id)
			} else {
				updatedContentIds.push(id)
			}
		})
		return [storedContentObject, updatedContentIds]
	}
	
	/**
	 * Fetch contents and update both current tree and contentStore
	 * @param objects Version objects
	 * @param currentFolderId string
	 * @returns Void
	 */
	const fetchContent = async (objects: any[], currentFolderTree: any, currentFolderId: any): Promise<any> => {
		if (currentFolderId !== folder_id) return;
		let contentIds: string[] = getCurrentIds(currentFolderTree, setReadmeObjectId, currentFolderId)
		// let contentIds: string[] = objects.map((obj: any) => obj.content_id) // too many characters
		let [storedContentObject, updatedContentIds] = getStoredContents(contentIds)
		// console.log("storedContentObject: ", storedContentObject, "updatedContentIds: ", updatedContentIds)
		let contentObject: contentObjects = {};
		if (updatedContentIds.length === 0) {
			contentObject = storedContentObject
		} else {
			try {
				let fetchedContentObject: any = await Content.getContents(userStore.get("user").username, updatedContentIds)
				// update store
				for (let obj in fetchedContentObject) {
					contentStore.set(obj, fetchedContentObject[obj])
				}
				contentObject = {...storedContentObject, ...fetchedContentObject}
			} catch (e: any) {
				console.log(e)
				return;
			}
		}
		objects = objects.map((obj: any) => ({...obj, content: contentObject[obj.content_id]}))
		const tree = new ObjectTree(objects).chonkyFileMap(assetName as string);
		setFileTree({...tree});
	}
	
	useEffect(() => {
		// Name
		setAssetName(props.asset.name(class_name as string));
		// Version
		const version = props.activeVersion;
		// console.log("Version objects: ", version?.objects)
		
		// Tree
		let versionObjects: AssetObject[] = version?.objects ? version.objects : [];
		// if (versionObjects) {
		//     const paths = versionObjects.map((obj: AssetObject) => obj.path());
		//     let currentFileTree = FileTree.pathsToTree(paths);
		//     console.log(FileTree.prettyPrintTree(currentFileTree))
		// }
		const tree = new ObjectTree(versionObjects).chonkyFileMap(assetName as string);
		setFileTree({...tree});
		if (folder_id && folder_id !== currentFolderId) {
			setCurrentFolderId(folder_id);
		} else {
			setCurrentFolderId(tree.rootFolderId);
		}
		// Fetch content and update tree
		fetchContent(versionObjects, tree, folder_id)
		
		// remove search input in dom
		if (toolbarRef.current) {
			toolbarRef.current.querySelector("input").value = '';
			// console.log("search:", toolbarRef.current.querySelector("input").value)
		}
	}, [props.activeVersion, folder_id])
	
	
	const map = fileTree ? fileMap(fileTree) : {};
	// console.log("fileMap:", fileTree);
	//console.log("map:", map);
	const files = useFiles(currentFolderId, map);
	// console.log("currentFolderId:", currentFolderId, " files:", files);
	const folderChain = useFolderChain(currentFolderId, map);
	// const handleFileAction = useFileActionHandler(setCurrentFolderId);
	const handleFileAction = useFileActionHandler(version_number);
	// console.log(`version:${version_number}, files:${files.map((o: any) => o.id).join("\n")}`);
	console.log("version:", version_number);
	
	/**
	 * Customize mouse click file action to remove search string
	 * before showing files of the child folder being searched
	 * ref: https://discord.com/channels/696033621986770957/696033622456532994/970612523063722005
	 */
	ChonkyActions.MouseClickFile = defineFileAction({
		...ChonkyActions.MouseClickFile,
	}, ({reduxDispatch}) => {
		reduxDispatch(reduxActions.setSearchString(''));
	})
	
	if (!version_number) {
		return <Navigate to={"/not_found"}/>
	}
	
	return (
		<div className="">
			<div className="h-[500px]">
				<FileBrowser
					key={props.asset.id}
					files={files}
					folderChain={folderChain}
                    iconComponent={FileIcon}
					// disableDefaultFileActions={[ChonkyActions.EnableGridView.id]}
					defaultFileViewActionId={ChonkyActions.EnableListView.id}
					fileActions={[ChonkyActions.MouseClickFile]}
					onFileAction={handleFileAction as any}
					// thumbnailGenerator={(file: FileData) =>
					//     file.thumbnailUrl ? `https://chonky.io${file.thumbnailUrl}` : null
					// }
				>
					{/*<FileNavbar/>*/}
					<div ref={toolbarRef}>
						<FileToolbar/>
					</div>
					<FileList/>
					<FileContextMenu/>
				</FileBrowser>
			</div>
			{readmeObjectId &&
                <div className={styles.card}>
                    <div className={styles.textBoxHeader}>
                        <div className={styles.tbHeaderContents}>
                            <div className={styles.readMeContainer}>
                                <span>README.md</span>
                            </div>
                        </div>
                    </div>
                    <div className={styles.readmeContainer}>
                        <ObjectBrowser asset={props.asset} objectId={readmeObjectId}
                                       view={"object"} header={false}/>
                    </div>
                </div>
			}
		</div>
	);
	
	function useFileActionHandler(version_number: any) {
		// console.log("version:", version_number);
		// console.log("location:", location);
		return (data: any) => {
			// console.log(data);
			chonkyAction(data);
			// console.log("location:", location);
			// console.log(data);
		}
	}
	
	function chonkyAction(data: ChonkyFileActionData) {
		console.log("location:", location);
		switch (data.id) {
			case ChonkyActions.OpenFiles.id: {
				const {targetFile, files} = data.payload;
				const fileToOpen = targetFile ?? files[0];
				if (fileToOpen && FileHelper.isDirectory(fileToOpen)) {
					// setCurrentFolderId(fileToOpen.id);
					navigateToFolderId(fileToOpen.id);
					return;
				}
				break;
			}
			case ChonkyActions.MouseClickFile.id: {
				const targetFile = data.payload.file;
				if (targetFile && FileHelper.isDirectory(targetFile)) {
					// setCurrentFolderId(targetFile.id);
					navigateToFolderId(targetFile.id);
					return;
				}
				break;
			}
			default: {
				break;
			}
		}
		showActionNotification(data);
	}
	
	
	// function useFileActionHandler2 (
	//     setCurrentFolderId: (folderId: string) => void){
	//     return useCallback(
	//         (data: ChonkyFileActionData) => {
	//             switch (data.id) {
	//                 case ChonkyActions.OpenFiles.id: {
	//                     const {targetFile, files} = data.payload;
	//                     const fileToOpen = targetFile ?? files[0];
	//                     if (fileToOpen && FileHelper.isDirectory(fileToOpen)) {
	//                         // setCurrentFolderId(fileToOpen.id);
	//                         navigateToFolderId(fileToOpen.id);
	//                         return;
	//                     }
	//                     break;
	//                 }
	//                 case ChonkyActions.MouseClickFile.id: {
	//                     const targetFile = data.payload.file;
	//                     if (targetFile && FileHelper.isDirectory(targetFile)) {
	//                         // setCurrentFolderId(targetFile.id);
	//                         navigateToFolderId(targetFile.id);
	//                         return;
	//                     }
	//                     break;
	//                 }
	//                 default: {
	//                     break;
	//                 }
	//             }
	//             showActionNotification(data);
	//         },
	//         [setCurrentFolderId]
	//     );
	// }
	
	function showActionNotification(data: any) {
		console.log("show notification:", data);
		if (data.payload && data.payload.file && data.payload.file.object_id) {
			console.log("navigating");
			let target = `${location.pathname}?version=${version_number}`;
			const objectId: string = data.payload.file.object_id;
			const encodedObject = encodeURIComponent(objectId);
			navigate(`${target}&object=${encodedObject}`)
		}
	}
	
	function navigateToFolderId(folderId: any) {
		console.log("navigate to folder: ", folderId);
		console.log("location:", location);
		console.log(folderId, version_number);
		let target = `${location.pathname}?version=${version_number}&folder=${encodeURIComponent(folderId)}`;
		navigate(target);
	}
}
