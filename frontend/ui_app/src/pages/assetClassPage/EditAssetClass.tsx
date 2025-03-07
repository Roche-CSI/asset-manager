import React, {useEffect, useState} from "react";
import styles from "./edit.module.scss";
import {isEmptyObject} from "../../utils";
import {AssetClass} from "../../servers/asset_server";
import {StoreNames, useStore} from "../../stores";
import {ErrorBoundary} from "../../components/errorBoundary";
import AssetClassEditForm from "./AssetClassEditForm";
import {Modal} from "react-bootstrap";

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
}

interface CreateProps {
    assetClass?: AssetClass;
    onSave: Function;
    onCancel: Function;
    show: boolean;
}

/**React-Bootstrap form validation
 * https://react-bootstrap.github.io/forms/validation/
 * @constructor
 */
export default function EditAssetClass(props: CreateProps) {
    const classIdStore = useStore(StoreNames.classIdStore);
    const classNameStore = useStore(StoreNames.classNameStore);
    const userStore = useStore(StoreNames.userStore);
    const [validated, setValidated] = useState(false);
    const [showForm, setShowForm] = useState(true);
    const [showAlert, setShowAlert] = useState(false);
    const [formData, setFormData] = useState<FormState>({
        id: null,
        name: "",
        title: "",
        description: "",
        class_type: "",
        has_readme: false,
        is_create: true,
        owner: "",
        created_at: ""
    });
    const [formErrors, setFormErrors] = useState<FormState>({});
    let readMe: any = null;

    useEffect(() => {
        if (props.assetClass) {
            setFormData((formData) => ({
                ...{
                    id: props.assetClass?.id,
                    name: props.assetClass?.name,
                    title: props.assetClass?.title !== 'n/a' ? props.assetClass?.title : "",
                    class_type: props.assetClass?.class_type,
                    description: props.assetClass?.description,
                    owner: props.assetClass?.owner,
                    created_at: props.assetClass?.created_at,
                    has_readme: Boolean(props.assetClass?.readme),
                    is_create: false
                }
            }));
            setFormErrors((formErrors) => ({}));
        }
        setShowForm(props.show);
        setValidated(false);
    }, [props.assetClass, props.show])

    const onFormHide = () => {
        console.log("on hide called");
        setShowForm(false);
        props.onCancel();
    }

    return (
        <div>
            <Modal show={showForm} onHide={onFormHide as any}>
                <div className={styles.page}>
                    <div className={styles.cardHeader}>
                        Edit AssetClass details
                    </div>
                    <ErrorBoundary>
                        <AssetClassEditForm onSave={handleSubmit}
                                            onCancel={onFormHide}
                                            onFieldChanged={onFormFieldChange}
                                            title={formData.title!}
                                            description={formData.description!}
                                            class_type={formData.class_type!}
                                            name={formData.name!}
                                            has_readme={formData.has_readme!}
                                            errors={formErrors}
                                            validated={validated}/>
                    </ErrorBoundary>
                </div>
            </Modal>
            {/*{showAlert && userAlert()}*/}
        </div>
    );


    function handleSubmit(event: any) {
        const form = event.currentTarget;
        event.preventDefault();
        event.stopPropagation();
        customValidation(form).then(errors => {
            if (!isEmptyObject(errors)) {
                setFormErrors((formErrors) => ({...(errors as FormState)}));
                setValidated(true);
                setShowAlert(false);
            } else {
                editAssetClass()
            }
        }).catch(err => setFormErrors((formErrors) => ({
            ...formErrors,
            unknown: JSON.stringify(err)
        })))
    }

    function editAssetClass() {
        let data: any = {};
        let editFields = ["title", "class_type", "description"];
        editFields.forEach((field: string, idx: number) => {
            if((formData as any)[field] !== (props.assetClass as any)[field]) {
                data[field] = (formData as any)[field];
            }
        })
        if (!isEmptyObject(data)) {
            data["user"] = userStore.get("user").username;
        }
        AssetClass.update(props.assetClass!.id, data, false).then(res => {
            let updated = new AssetClass(res as any);
            // console.log("updated:", updated);
            classIdStore.set(updated.id, updated);
            classNameStore.set(updated.name, updated); // update both
            setFormData((formData) => ({
                ...{
                    id: updated.id,
                    name: updated.name,
                    title: updated.title,
                    class_type: updated.class_type,
                    description: updated.description,
                    owner: props.assetClass?.owner,
                    created_at: props.assetClass?.created_at,
                    is_create: false
                }
            }));
            setValidated(true);
            setShowForm(false);
            setShowAlert(true);
            props.onSave();
        }).catch(error => setFormErrors((formErrors) => ({
            ...formErrors,
            unknown: error
        })));
    }


    function customValidation(form: any): Promise<any> {
        return new Promise((resolve, reject) => {
            let errors: any = {};
            for (const field in formData) {
                let val = (formData as any)[field];
                switch (field) {
                    case 'title': {
                        if (val === "" || val === 'n/a') {
                            errors[field] = "Title is required";
                        }
                        break;
                    }

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
                    default: {
                        break;
                    }
                }
            }
            resolve(errors);
        });
    }

    function onFormFieldChange(e: any, field: string) {
        let update: any = {};
        // console.log("on changed called: ", e, "field:", field);
        switch (field) {
            case "title": {
                update["title"] = e.target.value;
                break;
            }
            case "class_type":
            case "description": {
                update[field] = e.target.value;
                break;
            }
            default:
                break;
        }
        setFormData((formData: any) => ({...formData, ...update}))
    }

}