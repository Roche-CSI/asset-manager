import React, {useMemo, useState} from "react";
import {AssetClass} from "../../../servers/asset_server";
import {useStore, StoreNames} from "../../../stores";
import {ErrorBoundary} from "../../../components/errorBoundary";
import {AlertDismissible} from "../../../components/alerts";
import {DiamondPlus, Dices, ImagePlus} from "lucide-react";
import Spinner from "../../../components/spinner/Spinner.tsx";
import {useData, UseDataReturnType} from "../../../hooks/useData";
import Template, {TemplateData} from "../../../servers/asset_server/template";
import {WebhookCard} from "pages/assetClassPageV2/cards/WebhookCard";
import WebhookForm from "../forms/WebhookForm";

const sampleEvents = [
	{
		"entity_type": "asset",
		"entity_id": "DATASET_001",
		"name": "dataset_update",
		"title": "Protein Fasta Dataset Update",
		"description": "New version of the large language model training dataset available",
		"webhook_url": "https://api.mlops.example.com/webhooks/dataset-update",
		"event_type": "update",
		"attributes": {
			"status": "scheduled",
			"importance": "critical"
		}
	},
	{
		"entity_type": "project",
		"entity_id": "AI_MODEL_XYZ",
		"name": "ai_model_create",
		"title": "New Base Caller Model",
		"description": "Creating BaseCaller Models",
		"webhook_url": "https://api.mlops.example.com/webhooks/model-deployment",
		"event_type": "create",
		"attributes": {
			"status": "scheduled",
			"importance": "high"
		}
	},
	{
		"entity_type": "asset_collection",
		"entity_id": "IMAGE_DATASET_V2",
		"name": "dp_image_classification_deletion",
		"title": "Image Classification Dataset Delete",
		"description": "Deletion of image dataset for classification dataset",
		"webhook_url": "https://api.mlops.example.com/webhooks/dataset-collection-update",
		"event_type": "delete",
		"attributes": {
			"status": "scheduled",
			"importance": "medium"
		}
	},
	{
		"entity_type": "asset",
		"entity_id": "MODEL_WEIGHTS_001",
		"name": "neural_network_weights",
		"title": "Neural Network Weights Deprecation",
		"description": "Deprecating old neural network weights",
		"webhook_url": "https://api.mlops.example.com/webhooks/model-weights-deprecation",
		"event_type": "deprecate",
		"attributes": {
			"status": "deprecated",
			"importance": "medium"
		}
	},
	{
		"entity_type": "project",
		"entity_id": "NLP_PIPELINE_001",
		"name": "nlp_pipeline_deletion",
		"title": "NLP Pipeline Deletion",
		"description": "Removing deprecated NLP pipeline from the system",
		"webhook_url": "https://api.mlops.example.com/webhooks/pipeline-deletion",
		"event_type": "delete",
		"attributes": {
			"status": "scheduled",
			"importance": "high"
		}
	}
];

export const WebhookListView: React.FC<{ assetClass: AssetClass }> = ({assetClass}) => {
	const userStore = useStore(StoreNames.userStore);
	const active_project: string = userStore.get("active_project");
	
	const [error, setError] = useState<string>('');
	const [fetchTrigger, setFetchTrigger] = useState(0);
	const [searchTerm, setSearchTerm] = useState<string>("");
	
	const [addTemplate, setAddTemplate] = useState<boolean>(false);
	const [editTemplate, setEditTemplate] = useState<TemplateData | null>(null);
	
	const fetchPromise: Promise<TemplateData[]> = useMemo(() =>
		Template.getFromServer(userStore.get("user").username), [fetchTrigger, userStore]);
	// const fetchData: UseDataReturnType<TemplateData[]> = useData<TemplateData[]>(fetchPromise);
	const fetchData = {loading: false, error: null, data: sampleEvents}
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
			<div className="w-full mb-6">
				{fetchData.loading && <Spinner message={"Loading"}/>}
				{!fetchData.loading && !fetchData.error && (
					<div>
						<div className="flex items-center justify-between">
							<div className="flex space-x-4 w-full justify-between mb-6">
								<span className="text-neutral text-lg font-semibold">
									{addTemplate ? "Add Webhook" : "Webhooks List"}
								</span>
								<button
									className={`btn btn-sm btn-secondary rounded-md ${addTemplate || editTemplate ? "hidden" : ""}`}
									onClick={() => setAddTemplate(prevState => !prevState)}>
									Add Webhook
									<DiamondPlus className="size-4"/>
								</button>
							</div>
						</div>
						{(addTemplate || editTemplate) && (
							<div className="p-6 border border-base-300 rounded-md mb-6">
								<WebhookForm
									assetClass={assetClass}
									onSave={onFormSave}
									onCancel={onFormCancel}
									data={editTemplate ? editTemplate : null}
									action={editTemplate ? "edit" : "create"}
								/>
							</div>
						)}
						{(addTemplate || editTemplate) ? null : !fetchData.data ? null : (
							<div className="grid grid-cols-3 gap-6">
								{fetchData.data.map((item: any, idx: number) => (
									// <TemplateCard item={item} key={idx}/>
									<WebhookCard event={item}/>
									               // key={idx}
									               // onAction={onCardAction}
									               // projectId={active_project}
									               // assetClassName={assetClass.name}/>
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

export default WebhookListView;
