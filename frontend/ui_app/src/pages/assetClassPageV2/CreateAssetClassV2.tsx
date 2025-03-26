import React, { useEffect, useState } from "react";
import { AssetClass } from "../../servers/asset_server";
import { StoreNames, useStore } from "../../stores";
import { ErrorBoundary } from "../../components/errorBoundary";
import { useLocation, useNavigate } from "react-router-dom";
import { BreadCrumbV2 } from "../../components/breadCrumb/BreadCrumbV2";
import { TabBar } from "../../components/tabbar";
import {
    Image,
    BookText, Dices,
    FileCog,
    Info
} from "lucide-react";
import { AssetClassForm } from "./forms/AssetClassForm.tsx";
import AssetClassView from "pages/assetClassPageV2/tabs/AssetClassView.tsx";
import TemplateListView from "pages/assetClassPageV2/tabs/TemplateListView.tsx";
import ReadMeView from "pages/assetClassPageV2/tabs/ReadMeView.tsx";
import WebhookListView from "pages/assetClassPageV2/tabs/WebhookListView.tsx";
import MetaSchemaView from "pages/assetClassPageV2/tabs/MetaSchemaView.tsx";


export const CreateAssetClassV2: React.FC<{ projectId: string }> = ({ projectId }) => {

    const classIdStore = useStore(StoreNames.classIdStore);
    const classNameStore = useStore(StoreNames.classNameStore);
    const userStore = useStore(StoreNames.userStore);

    const project: any = userStore.get("projects")[projectId];

    const location = useLocation();
    const params = new URLSearchParams(location.search);
    const activeTab = params.get("tab") || "info";

    const [assetClass, setAssetClass] = useState<AssetClass | null>(null);

    const navigate = useNavigate();

    /**
     * Users might open the asset creation page through python CLI
     * Need to update current project selection if necessary
     */
    useEffect(() => {
        if (projectId !== userStore.get("active_project")) {
            if (Object.keys(userStore.get("projects")).includes(projectId)) {
                userStore.set("active_project", projectId)
                classIdStore.didFullUpdate = false; //force update class list
            }
        }
    })

    const Nav = [
        { name: project.name, url: "/projects", label: project.description, index: 0 },
        { name: "asset_classes", url: "/assets", index: 1, label: "Asset Collections" },
        { name: "create", url: "", index: 2, label: "Create" }
    ]

    const urlForTab = (tab: string) => {
        const searchParams = location.search.includes("tab") ? location.search.replace(`tab=${activeTab}`, `tab=${tab}`) :
            location.search + `&tab=${tab}`
        return `${location.pathname}${searchParams}`;
    }

    const TABS = [
        { name: "info", label: "About", icon: <Info className="size-3 mr-2" />, link: urlForTab("info") },
        { name: "readme", label: "ReadMe", icon: <BookText className="size-3 mr-2" />, link: urlForTab("readme"), disabled: !Boolean(assetClass) },
        { name: "templates", label: "Templates", icon: <Image className="size-3 mr-2" />, link: urlForTab("templates"), disabled: !Boolean(assetClass) },
        { name: "webhooks", label: "Webhooks", icon: <Dices className="size-3 mr-2" />, link: urlForTab("webhooks"), disabled: !Boolean(assetClass) },
        { name: "meta_schema", label: "Meta Schema", icon: <FileCog className="size-3 mr-2" />, link: urlForTab("meta_schema"), disabled: !Boolean(assetClass) },
    ];

    const onCreate = (data) => {
        console.log("created:", data);
        let created = new AssetClass(data as any);
        classIdStore.set(created.id, created);
        classNameStore.set(created.name, created);
        setAssetClass(created);
    }

    const onCancel = () => {
        navigate("/assets/all");
    }

    const darkStyle = "dark:border-slate-800 dark:bg-slate-800 dark:text-white";
    const TabView = (tab) => {
        switch (tab) {
            case "info":
                return (
                    <React.Fragment>
                        {assetClass ? (
                            <AssetClassView assetClass={assetClass} />
                        ) : (
                            <React.Fragment>
                                <div className="text-lg text-neutral mb-6 font-semibold">
                                    Create Asset Collection
                                </div>
                                <div className="mb-6 bg-white w-full rounded-lg border border-base-300 p-6 hover:shadow-md">
                                    <AssetClassForm
                                        action="create"
                                        project={project}
                                        onSave={onCreate}
                                        onCancel={onCancel}
                                    />
                                </div>
                            </React.Fragment>
                        )}
                    </React.Fragment>
                )
            case "templates":
                return <TemplateListView assetClass={assetClass} />;
            case "readme":
                return <ReadMeView assetClass={assetClass} />;
            case "webhooks":
                return <WebhookListView assetClass={assetClass} />;
            case "meta_schema":
                return <MetaSchemaView assetClass={assetClass} />;
            default:
                return <div>Default</div>;
        }
    }

    return (
        <div className=''>
            <div className="bg-base-200 pt-6 px-16">
                <div className="mx-auto">
                    <div className="flex flex-col space-y-4">
                        <BreadCrumbV2 items={Nav} />
                        <h2 className="text-lg text-neutral">
                            {assetClass ? assetClass.title : 'New Asset Collection'}
                        </h2>
                        <TabBar tabs={TABS} activeTab={activeTab} />
                    </div>
                </div>
            </div>
            <div className='px-16 pt-6'>
                <ErrorBoundary>
                    {TabView(activeTab)}
                </ErrorBoundary>
            </div>
        </div>
    );
}
