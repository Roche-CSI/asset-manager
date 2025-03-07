import React, {useMemo, useState} from "react";
import {AssetClass} from "../../../servers/asset_server";
import {useStore, StoreNames} from "../../../stores";
import {ErrorBoundary} from "../../../components/errorBoundary";
import {AlertDismissible} from "../../../components/alerts";
import {ImagePlus} from "lucide-react";
import Spinner from "../../../components/spinner/Spinner";
import {TemplateForm} from "../forms/TemplateForm";
import {useData, UseDataReturnType} from "../../../hooks/useData";
import Template, {TemplateData} from "../../../servers/asset_server/template";
import TemplateCard2 from "pages/assetClassPageV2/cards/TemplateCard2";

export const TemplateListView: React.FC<{ assetClass: AssetClass }> = ({assetClass}) => {
	const userStore = useStore(StoreNames.userStore);
	const active_project: string = userStore.get("active_project");
	
	const [error, setError] = useState<string>('');
	const [fetchTrigger, setFetchTrigger] = useState(0);
	const [searchTerm, setSearchTerm] = useState<string>("");
	
	const [addTemplate, setAddTemplate] = useState<boolean>(false);
	const [editTemplate, setEditTemplate] = useState<TemplateData | null>(null);
	
	const fetchPromise: Promise<TemplateData[]> = useMemo(() =>
		Template.getFromServer(userStore.get("user").username), [fetchTrigger, userStore]);
	const fetchData: UseDataReturnType<TemplateData[]> = useData<TemplateData[]>(fetchPromise);
	console.log("fetchData:", fetchData);
	
	const unknownError = (error: string) => (
		<div className="">
			<AlertDismissible>
				{error}
			</AlertDismissible>
		</div>
	);
	
	const onFormSave = (data: TemplateData) => {
		console.log("Template added successfully:", data);
		setFetchTrigger(prevState => prevState + 1);
		setAddTemplate(false);
		setEditTemplate(null);
	}
	
	const onCardAction = (action: string, template: TemplateData) => {
		console.log("Action:", action, " template:", template);
		if (action === "edit") {
			setEditTemplate(template);
		} else if (action === "delete") {
			//refresh
			setFetchTrigger(prevState => prevState + 1);
		}
	}
	
	const onFormCancel = () => {
		setAddTemplate(false);
		setEditTemplate(null);
	}
	
	return (
		<ErrorBoundary>
			<div className="w-full">
				{fetchData.loading && <Spinner message={"Loading"}/>}
				{!fetchData.loading && !fetchData.error && (
					<div>
						<div className="flex items-center justify-between">
							<div className="flex space-x-4 w-full justify-between mb-6">
                                <span className="text-neutral text-lg font-semibold">
                                    {addTemplate ? "Add Template" : "Templates List"}
                                </span>
								<button
									className={`btn btn-sm btn-secondary rounded-md ${addTemplate || editTemplate ? "hidden" : ""}`}
									onClick={() => setAddTemplate(prevState => !prevState)}>
									Add Template
									<ImagePlus className="size-4"/>
								</button>
							</div>
						</div>
						{(addTemplate || editTemplate) && (
							<div className="p-6 border border-base-300 rounded-md mb-6">
								<TemplateForm
									assetClass={assetClass}
									onSave={onFormSave}
									onCancel={onFormCancel}
									data={editTemplate ? editTemplate : null}
									action={editTemplate ? "edit" : "create"}
								/>
							</div>
						)}
						{(addTemplate || editTemplate) ? null : !fetchData.loading && fetchData?.data?.length === 0 ? 
							<div className="h-32 border border-base-300 rounded-md w-full">
                        		<div className="flex justify-center items-center h-full text-neutral-500">
                            		No Templates content available
                        		</div>
							</div>
							: (
							<div className="grid grid-cols-6 gap-6">
								{fetchData.data.map((item: any, idx: number) => (
									// <TemplateCard item={item} key={idx}/>
									<TemplateCard2 item={item}
									               key={idx}
									               onAction={onCardAction}
									               projectId={active_project}
									               assetClassName={assetClass.name}/>
								))}
							</div>
						)}
					</div>
				)}
				{error && unknownError(error)}
			</div>
		</ErrorBoundary>
	);
};

export default TemplateListView;
