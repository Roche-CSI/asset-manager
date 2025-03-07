import React, {useEffect, useState} from "react";
import styles from "./create.module.scss";
import {convertToCurrentTimeZone, isEmptyObject} from "../../utils";
import {AssetClass} from "../../servers/asset_server";
import {AlertDismissible} from "../../components/alerts";
import {StoreNames, useStore} from "../../stores";
import {FieldsTable} from "../../components/tables";
import AssetClassFormTemplate from "./AssetClassFormTemplate"
import {ErrorBoundary} from "../../components/errorBoundary";
import {Link, useNavigate} from "react-router-dom";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {Button, Spinner} from "react-bootstrap";
import Breadcrumb, { BreadcrumbItem } from "../../components/breadCrumb/Breadcrumb";
import { formatAssetClassName, validateAssetClassName } from "./utils";
import {BreadCrumbV2} from "../../components/breadCrumb/BreadCrumbV2.tsx";
import {TabBar} from "../../components/tabbar";
import {HoveringCodeBlock} from "../../components/hoveringCodeBlock";
import {bashCode, pythonCode} from "../assetPageV2/code.tsx";
import {ThreeBarsIcon, ArtifactsIcon} from "../../components/icons/Icons.tsx";
import {WaypointsIcon} from "lucide-react";

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

interface CreateProps {
    project_id: string;
}

enum CREATE_STATUS {
    NOT_STARTED = 0,
    STARTED,
    COMPLETED
}

export default function CreateAssetClass(props: CreateProps) {
    const classIdStore = useStore(StoreNames.classIdStore);
    const classNameStore = useStore(StoreNames.classNameStore);
    const userStore = useStore(StoreNames.userStore);
    const [validated, setValidated] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    const [createStatus, setCreateStatus] = useState(CREATE_STATUS.NOT_STARTED);
    const navigate = useNavigate();
    const [formData, setFormData] = useState<FormState>({
        id: null,
        name: "",
        title: "",
        description: "",
        class_type: "",
        has_readme: false,
        is_create: true,
        owner: "",
        created_at: "",
        project_id: props.project_id,
        project_name: userStore.get("projects")?.[props.project_id]?.name
    });
    const [formErrors, setFormErrors] = useState<FormState>({});
    let readMe: any = null;

    /**
     * Users might open the asset creation page through python CLI
     * Need to update current project selection if necessary
     */
    useEffect(() => {
        if (props.project_id !== userStore.get("active_project")) {
            if (Object.keys(userStore.get("projects")).includes(props.project_id)) {
                userStore.set("active_project", props.project_id)
                classIdStore.didFullUpdate = false; //force update class list
            }
        }
    })

    useEffect(() => {
        if (createStatus === CREATE_STATUS.NOT_STARTED) {
            setFormErrors((formErrors) => ({}));
        }else if (createStatus === CREATE_STATUS.COMPLETED) {
            navigate(`/asset_class?project_id=${props.project_id}&name=${formData.name}`)
        }
    }, [createStatus])
    
    const Nav = [
        {name: "", url: "/projects", label: "", index: 0},
        {name: "asset_classes", url: "/assets", index: 1, label: "Asset Collections"},
        {name: "create", url: "", index: 2, label: "Create Collection"}
    ]
    
    const TABS = [
        {name: 'about', icon: <ThreeBarsIcon className="h-3 w-3 mr-2"/>, label: "About", link: "/assets/all"},
        {name: 'card', icon: <ThreeBarsIcon className="h-3 w-3 mr-2"/>, label: "ReadME", link: "/assets/all"},
        {name: 'templates', icon: <ArtifactsIcon className="h-3 w-3 mr-2"/>, label: "Templates", link: "/assets/data"},
        {name: 'events', icon: <WaypointsIcon className="h-3 w-3 mr-2"/>, label: "Events", link: "/assets/models"},
    ]

    return (
        <div className=''>
            <div className="bg-base-200 pt-6 px-16">
                <div className="mx-auto">
                    <div className="flex flex-col space-y-4">
                        <BreadCrumbV2 items={Nav}/>
                        <h2 className="text-lg text-neutral">
                            Create Asset Collection
                        </h2>
                        <TabBar tabs={TABS} activeTab={"data"}/>
                    </div>
                </div>
            </div>
            {/* {pageTitle("create")} */}
            <div className='flex flex-col gap-9'>
                <ErrorBoundary>
                    <AssetClassFormTemplate onSubmit={handleSubmit}
                                            onFieldChanged={onFormFieldChange}
                                            title={formData.title!}
                                            description={formData.description!}
                                            class_type={formData.class_type!}
                                            name={formData.name!}
                                            has_readme={formData.has_readme!}
                                            project_id={formData.project_id!}
                                            project_name={formData.project_name!}
                                            errors={formErrors}
                                            validated={validated}/>
                </ErrorBoundary>
            </div>
            {showAlert && userAlert()}
            {createStatus === CREATE_STATUS.STARTED && spinner()}
        </div>
    );
    
    function pageTitle(className: string) {
        return (
            <div style={{border: "none", display: "flex"}}>
                <div className={styles.pageHeader}>
                    <h5>
                        <Link to="/assets">assets</Link>
                        <ArrowRightIcon/>
                        <span>{className}</span>
                    </h5>
                </div>
            </div>
        )
    }
    
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
    
    function spinner() {
        return (
            <div className={styles.spinnerContainer}>
                <Button variant="primary" disabled>
                <Spinner
                        as="span"
                        animation="grow"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                    />
                    Creating...
                </Button>
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
