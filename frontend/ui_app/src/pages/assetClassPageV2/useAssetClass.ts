import { useState, useEffect } from "react";
import { StoreNames, useStore } from "../../stores";
import { useQuery } from "../../utils/utils";
import { AssetClass } from "../../servers/asset_server";

export const useAssetClass = (projectId: string) => {
	const classNameStore = useStore(StoreNames.classNameStore);
	const classIdStore = useStore(StoreNames.classIdStore);
	const userStore = useStore(StoreNames.userStore);
	const assetClassName = useQuery().get("name");
	const [assetClass, setAssetClass] = useState<AssetClass | null>(() =>
		assetClassName ? classNameStore.get(assetClassName) : null
	);
	const [error, setError] = useState<string | null>(null);
	
	useEffect(() => {
		const activeProjectId = userStore.get("active_project");
		
		if (projectId !== activeProjectId) {
			const userProjects = userStore.get("projects");
			if (Object.keys(userProjects).includes(projectId)) {
				userStore.set("active_project", projectId);
			} else {
				setError("Oops! You do not have access to the project where this asset class is located");
				return;
			}
		}
		
		if (assetClassName) {
			if (!classNameStore.get(assetClassName)) {
				AssetClass.getFromServer(null, assetClassName, projectId)
					.then((json) => {
						const newClass = new AssetClass(json[0]);
						classNameStore.set(assetClassName, newClass);
						classIdStore.set(newClass.id, newClass);
						setAssetClass(newClass);
					})
					.catch((error: any) => {
						console.error("Failed to fetch asset class:", error.message);
						setError("Asset Class Not Found In Current Project");
					});
			} else {
				setAssetClass(classNameStore.get(assetClassName));
			}
		}
	}, [assetClassName, projectId, classNameStore, classIdStore, userStore]);
	
	return { assetClass, error };
};
