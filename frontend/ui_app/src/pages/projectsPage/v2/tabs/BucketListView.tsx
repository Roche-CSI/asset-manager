import React, {useEffect, useMemo, useState} from "react";
import {BucketData} from "../../../../servers/asset_server/bucket";
import BucketCard    from "pages/projectsPage/v2/cards/BucketCard";
import { StoreNames, useStore } from "../../../../stores";
import {PackagePlus, Search} from "lucide-react";
import {useData, UseDataReturnType} from "../../../../hooks/useData";
import Spinner from "../../../../components/spinner/Spinner";
import {Alert} from "../../../../components/errorBoundary";
import Project, {ProjectData} from "../../../../servers/asset_server/project";
import {BucketForm} from "pages/projectsPage/v2/forms/BucketForm.tsx";

const EmptyBucket: BucketData = {
	id: "",
	bucket_url: "",
	is_active: true,
	keys: {},
	description: "",
	created_at: "",
	created_by: "",
	is_primary: false,
	configs: {}
	
}


const BucketListView: React.FC<{project: ProjectData}> = ({project}) => {
	const [fetchTrigger, setFetchTrigger] = useState(0);
	const [searchTerm, setSearchTerm] = useState<string>("");
	
	const userStore = useStore(StoreNames.userStore);
	const fetchPromise: Promise<BucketData[]> = useMemo(() => Project.getBucketsList(userStore.get("user").username, project.id), [fetchTrigger]);
	const fetchData: UseDataReturnType<BucketData[]> = useData<BucketData[]>(fetchPromise);
	
	const [addBucket, setAddBucket] = useState<boolean>(false);
	const [editBucket, setEditBucket] = useState<BucketData | null>(null);
	
	const currentUser = userStore.get("user")
	const isAdmin: boolean = userStore.get("projects")?.[project?.id]?.can_admin_project || currentUser.is_admin;
	
	if (!project || !currentUser) {
		return null;
	}
	
	const handleDelete = (bucket: BucketData) => {
		Project.removeBucket(bucket.id, userStore.get('user').username, project.id)
			.then((data: any) => {
				console.log("Bucket removed from project successfully:", data);
				setFetchTrigger(prevState => prevState + 1);
			}).catch((error: any) => {
			console.error("Error deleting bucket:", error);
		});
	}
	
	const onBucketSave = (data) => {
		setFetchTrigger(prevState => prevState + 1);
		setAddBucket(false);
	};
	
	const handleEdit = (bucket: BucketData) => {
		setEditBucket(bucket);
	}
	
	if (fetchData.loading) {
		return <Spinner message={"Loading..."} />;
	}
	
	if (fetchData.error) {
		return <Alert title={"Oh Snap! There is an error"} variant={"error"} message={fetchData.error.toString()} />;
	}
	
	if (!fetchData.data) {
		return <span>No data found</span>;
	}
	
	const filteredBuckets = fetchData.data.filter(bucket =>
		bucket.bucket_url.includes(searchTerm.toLowerCase())
	);
	
	return (
		<div className="bg-base-100">
			<div className="flex justify-between">
				<div className="flex text-neutral-600 mb-4 space-x-4">
					<div className="flex space-x-4">
						<div className="text-lg text-neutral mb-6 font-semibold">Project Buckets</div>
						<span className="text-neutral-400 mt-0.5">#{fetchData.data.length}</span>
					</div>
					<div className="mb-4 relative">
						<input
							type="text"
							placeholder="Search buckets..."
							value={searchTerm}
							onChange={(e) => setSearchTerm(e.target.value)}
							className="w-full text-xs py-1 pl-10 pr-4 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<Search className="absolute -mt-1 left-2 top-1/2 transform -translate-y-1/2 size-4 text-gray-400"/>
					</div>
				</div>
				{
					(isAdmin && !editBucket) && (
						<button
							className={`btn btn-sm rounded-md ${addBucket ? "btn-ghost border border-secondary" : "btn-secondary"}`}
							onClick={() => setAddBucket(prevState => !prevState)}>
							Add Bucket
							<PackagePlus className="size-4"/>
						</button>
					)
				}
			</div>
			{
				(addBucket || editBucket) && (
					<div className="border border-base-300 p-6 max-w-2xl rounded-md mb-6">
						<div className="text-neutral-700 mb-4">Add Bucket to Project</div>
						<BucketForm
							adminUser={currentUser}
							data={editBucket ? editBucket : EmptyBucket}
							project={project}
							onSave={onBucketSave}
							action={editBucket ? "edit": "create"}
							onCancel={() => editBucket ? setEditBucket(null) : setAddBucket(false)}/>
					</div>
				)
			}
			{
				!(addBucket || editBucket) && (
					<div className="grid grid-cols-3 gap-6">
						{filteredBuckets.map((bucket: BucketData, idx: number) => (
							<BucketCard bucket={bucket} key={idx} onDelete={handleDelete} onEdit={handleEdit}/>
						))}
					</div>
				)
			}
		</div>
	);
}

export default BucketListView;
