import React, {useEffect, useState} from "react";
import {convertToCurrentTimeZone, isEmptyObject} from "../../utils";
import {AssetClass} from "../../servers/asset_server";
import {AlertDismissible} from "../../components/alerts";
import {StoreNames, useStore} from "../../stores";
import {FieldsTable} from "../../components/tables";
import {ErrorBoundary} from "../../components/errorBoundary";
import {Link, useLocation, useNavigate, useParams} from "react-router-dom";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {BreadCrumbV2} from "../../components/breadCrumb/BreadCrumbV2";
import {TabBar} from "../../components/tabbar";
import {
    Image,
    BookText, Dices,
    FileCog,
    Info,
    Menu,
    Pickaxe,
    WaypointsIcon
} from "lucide-react";
import {AssetClassForm} from "./forms/AssetClassForm.tsx";
import AssetClassView from "pages/assetClassPageV2/tabs/AssetClassView.tsx";
import {validateAssetClassName} from "pages/assetClassPage/utils.ts";
import TemplateListView from "pages/assetClassPageV2/tabs/TemplateListView.tsx";
import ReadMeView from "pages/assetClassPageV2/tabs/ReadMeView.tsx";
import WebhookListView from "pages/assetClassPageV2/tabs/WebhookListView.tsx";
import MetaSchemaView from "pages/assetClassPageV2/tabs/MetaSchemaView.tsx";

interface FormState {
    id?: string | null | undefined;
    title?: string;
    class_type?: string;
    name?: string;
    description?: string;
    has_readme?: boolean;
    is_create?: boolean;
    owner?: string;
    created_at?: string;
    project_id?: string;
    project_name?: string;
}

enum CREATE_STATUS {
    NOT_STARTED = 0,
    STARTED,
    COMPLETED
}


export const CreateAssetClassV2: React.FC<{projectId: string}> = ({projectId}) => {
    
    const classIdStore = useStore(StoreNames.classIdStore);
    const classNameStore = useStore(StoreNames.classNameStore);
    const userStore = useStore(StoreNames.userStore);
    
    const project: any = userStore.get("projects")[projectId];
    
    const location = useLocation();
    const params = new URLSearchParams(location.search);
    const activeTab = params.get("tab") || "info";
    
    const [assetClass, setAssetClass] = useState<AssetClass | null>(null);
    
    const [showAlert, setShowAlert] = useState(false);
    const [createStatus, setCreateStatus] = useState(CREATE_STATUS.NOT_STARTED);
    const navigate = useNavigate();
    
    let readMe: any = null;

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
        {name: project.name, url: "/projects", label: project.description, index: 0},
        {name: "asset_classes", url: "/assets", index: 1, label: "Asset Collections"},
        {name: "create", url: "", index: 2, label: "Create"}
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
                                <div className="bg-white w-full rounded-lg border border-base-300 p-6 hover:shadow-md">
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
                return <WebhookListView assetClass={assetClass}/>;
            case "meta_schema":
                return <MetaSchemaView assetClass={assetClass}/>;
            default:
                return <div>Default</div>;
        }
    }

    return (
        <div className=''>
            <div className="bg-base-200 pt-6 px-16">
                <div className="mx-auto">
                    <div className="flex flex-col space-y-4">
                        <BreadCrumbV2 items={Nav}/>
                        <h2 className="text-lg text-neutral">
                            New Asset Collection
                        </h2>
                        <TabBar tabs={TABS} activeTab={activeTab}/>
                    </div>
                </div>
            </div>
            {/* {pageTitle("create")} */}
            <div className='px-16 pt-6'>
                <ErrorBoundary>
                    {TabView(activeTab)}
                </ErrorBoundary>
            </div>
            {showAlert && userAlert()}
        </div>
    );
    
    function userAlert() {
        return (
            <div className={styles.overlayContainer}>
                <AlertDismissible className={styles.alert}
                                  title={"Success!"}
                                  successLabel={"Done"}
                                  cancelLabel={"Create more"}
                                  variant={"light"}>
                    {classFields(formData)}
                </AlertDismissible>
            </div>
        )
    }

    function classFields(data: any) {
        let display = {
            "Title": data.title,
            "Id": data.id,
            "Name": data.name,
            "Description": data.description,
            "Owner": data.owner,
            "Created": convertToCurrentTimeZone(data.created_at, "date")
        }
        return (
            <div>
                <FieldsTable fields={Object.entries(display)} title={["data", ""]}/>
            </div>
        )
    }

    function handleSubmit(event: any){
        const form = event.currentTarget;
        event.preventDefault();
        event.stopPropagation();
        customValidation(form).then(errors => {
            if (!isEmptyObject(errors)) {
                setFormErrors((formErrors) => ({...(errors as FormState)}));
                setValidated(true);
                setShowAlert(false);
            }else {
                createAssetClass()
            }
        }).catch(err => setFormErrors((formErrors) => ({
            ...formErrors,
            unknown: JSON.stringify(err)
        })))
    }

    function createAssetClass() {
        let data = {
            name: formData.name,
            user: userStore.get("user").username,
            class_type: formData.class_type,
            description: formData.description,
            readme: readMe,
            title: formData.title,
            project_id: formData.project_id
        }
        setCreateStatus(CREATE_STATUS.STARTED);
        AssetClass.create(data, false).then(res => {
            let created = new AssetClass(res as any);
            classIdStore.set(created.id, created);
            classNameStore.set(created.name, created); // retain both id and name mappings
            setCreateStatus(CREATE_STATUS.COMPLETED)
        }).catch(error => {
            setCreateStatus(CREATE_STATUS.COMPLETED);
            setFormErrors((formErrors) => ({
                ...formErrors,
                unknown: error
            }))
        });
    }


    function customValidation(form: any): Promise<any> {
        return new Promise((resolve, reject) => {
            let errors: any = {};
            for (const field in formData) {
                let val = (formData as any)[field];
                switch (field) {
                    case 'class_type': {
                        if (val === "") {
                            errors[field] = "Please select the type";
                        }
                        break;
                    }
                    case 'description': {
                        if (val === "") {
                            errors[field] = "Description is required"
                        }
                        break;
                    }
                    case 'name': {
                        if (val === "") {
                            errors[field] = "Name is required"
                        } else if (!validateAssetClassName(val)) {
                            errors[field] = "Name must be fewer than 52 characters, and only consists of lower case letters, digits, underscore, hyphen, or dot"
                        }
                        break;
                    }
                    case "project_id": { // validate user has access to project
                        if (!Object.keys(userStore.get("projects")).includes(val)) {
                            errors[field] = "You do not have access to the current project"
                        }
                        break;
                    }
                    default: {
                        break;
                    }
                }
            }
            if (!isEmptyObject(errors)) {
                resolve(errors);
            } else {
                // check in asset_server
                AssetClass.getFromServer(null, formData.name, formData.project_id).then((data: any) => {
                    console.log("asset classes found:", data);
                    if (data.length > 0) {
                        errors["name"] = "id conflict, asset class already exists"
                        errors["title"] = "use a different class title"
                    }
                    resolve(errors)
                }).catch(err => {
                    reject(err.message)
                })
            }
        });
    }

    function onFormFieldChange(e: any, field: string) {
        let update: any = {};
        // console.log("on changed called: ", e, "field:", field);
        switch (field) {
            case "title": {
                update["title"] = e.target.value;
                update["name"] = formatAssetClassName(e.target.value);
                break;
            }
            case "class_type":
            case "name":
            case "description": {
                update[field] = e.target.value;
                break;
            }
            case "has_readme": {
                update["has_readme"] = formData.has_readme ? false : true;
                break;
            }
            default:
                break;
        }
        setFormData((formData: any) => ({...formData, ...update}))
    }

}
