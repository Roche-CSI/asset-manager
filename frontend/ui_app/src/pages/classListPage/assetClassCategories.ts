import {CLASS_TYPE} from "../../components/assetClassBrowser/index.tsx";
import {AccessStatus} from "../../servers/base/accessStatus.ts";

export interface AssetClassCategory {
	idx: number,
	class_type: string,
	label: string,
	filterFunction: (item: any) => boolean
}

export const assetClassCategories: AssetClassCategory[] = [
	{
		idx: 0, class_type: 'all', label: 'All', filterFunction: (item: any) => item
	},
	{
		idx: 1,
		class_type: CLASS_TYPE.GENERAL,
		label: 'Data',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.GENERAL
	},
	{
		idx: 2,
		class_type: CLASS_TYPE.MODELS,
		label: 'Models',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.MODELS
	},
	{
		idx: 3,
		class_type: CLASS_TYPE.DOCKER,
		label: 'Containers',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.DOCKER
	},
	{
		idx: 4,
		class_type: CLASS_TYPE.CONFIGURATION,
		label: 'Configuration',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.CONFIGURATION
	},
	{
		idx: 5,
		class_type: CLASS_TYPE.IMAGES,
		label: 'Images',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.IMAGES
	},
	{
		idx: 6,
		class_type: CLASS_TYPE.REPORTS,
		label: 'Reports',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.REPORTS
	},
	{
		idx: 7,
		class_type: CLASS_TYPE.PIPELINES,
		label: 'Pipelines',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.PIPELINES
	},
	{
		idx: 8,
		class_type: CLASS_TYPE.EXPERIMENTAL,
		label: 'Experimental',
		filterFunction: (item: any) => item.class_type === CLASS_TYPE.EXPERIMENTAL
	},
	{
		idx: 9,
		class_type: CLASS_TYPE.DEPRECATED,
		label: 'Deprecated',
		filterFunction: (item: any) => item.status === AccessStatus.DEPRECATED.value
	},
	{
		idx: 10,
		class_type: CLASS_TYPE.OBSOLETE,
		label: 'Obsolete',
		filterFunction: (item: any) => item.status === AccessStatus.OBSOLETE.value
	},
	{
		idx: 11,
		class_type: "",
		label: 'Private',
		filterFunction: (item: any) => item.status === AccessStatus.PRIVATE.value
	},
	{
		idx: 12,
		class_type: "",
		label: 'Favorites',
		filterFunction: (item: any) => item.favorite
	},
]
