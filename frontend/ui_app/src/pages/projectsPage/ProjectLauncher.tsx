import React, { useState } from "react";
import { Modal } from "react-bootstrap";
import ProjectForm, { DisplayInfo } from "./ProjectForm";
import { ProjectFormData } from "./formControls";
import styles from "./launcher.module.scss";
import { StoreNames, useStore } from "../../stores";
import { SimpleToast } from "../../components/toasts";
import { ToastType } from "../../components/toasts/SimpleToast";
import { Project } from "../../servers/asset_server";

interface Props {
    onLaunch: Function;
    onCancel: Function;
    project?: any;
    readonly?: boolean;
    type: string;
}

export default function ProjectLauncher(props: Props) {
    // states
    const userStore = useStore(StoreNames.userStore);
    const [toastStatus, setToastStatus] = useState({ type: "", message: "" });
    // stores
    const projectStore = useStore(StoreNames.projectStore);

    const createNewProject = (data: any) => {
        Project.create(userStore.get("user").username, data
        ).then((res: any) => {
            console.log("res:", res);
            projectStore.set(res.id, res);
            props.onLaunch("success");
        }
        ).catch((error) => {
            console.log(error);
            setToastStatus({ type: "error", message: "Snap! There was an error. Please check your crendentials" });
            props.onLaunch("error");
        });
    }

    const updateProject = (data: any) => {
        Project.update(props.project.id, userStore.get("user").username, data
        ).then((res: any) => {
            console.log("res:", res);
            projectStore.set(res.id, res);
            props.onLaunch("success");
        }
        ).catch((error) => {
            console.log(error);
            setToastStatus({ type: "error", message: error.data.error });
            props.onLaunch("error");
        });
    }

    const onSubmit = (data: any) => {
        console.log("on_submit:", data);
        switch (props.type) {
            case "new":
                createNewProject(data);
                break;
            case "edit": {
                updateProject(data);
                break;
            }
        }
    }

    const onCancel = () => {
        props.onCancel();
    }

    const launchForm = () => {
        const input_data = props.project ? props.project : {};
        const formData: ProjectFormData = {
            ...input_data,
            user: input_data.user || userStore.get("user").username,
            modified_by: input_data.modified_by || userStore.get("user").username,
            name: input_data.name || '',
            description: input_data.description || '',
            is_active: input_data.is_active || true,
            staging_url: input_data.staging_url || '',
            remote_url: input_data.remote_url || '',
            credentials_user: input_data.credentials_user || '',
            credentials_server: input_data.credentials_server || '',
        }
        const displayInfo: DisplayInfo = {
            description: input_data.description || 'Create New Project',
            readonly: false,
            retry: Boolean(toastStatus.type),
        }
        return (
            <ProjectForm formData={formData}
                displayInfo={displayInfo}
                onSubmit={onSubmit}
                onCancel={onCancel} />
        )
    }

    const toast = () => {
        if (toastStatus.type) {
            return (
                <SimpleToast title={toastStatus.type}
                    message={toastStatus.message}
                    type={toastStatus.type === "error" ? ToastType.Danger : ToastType.Success}
                    onClose={() => setToastStatus({ type: "", message: "" })}
                    autoHide={false}
                    show={Boolean(toastStatus.type)}
                    position={"middle-center"} />
            );
        } else {
            return null;
        }
    }

    return (
        <Modal show={true}
            onHide={onCancel}
            className={styles.container}
            centered
            size="lg">
            {launchForm()}
            {toast()}
        </Modal>
    );
}