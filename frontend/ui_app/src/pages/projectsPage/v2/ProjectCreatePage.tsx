import React, { useState } from "react";
import ProjectForm, { DisplayInfo } from "../ProjectForm";
import { ProjectFormData } from "../formControls";
import { StoreNames, useStore } from "../../../stores";
import { SimpleToast } from "../../../components/toasts";
import { ToastType } from "../../../components/toasts/SimpleToast";
import { Project } from "../../../servers/asset_server";
import { ErrorBoundary } from "../../../components/errorBoundary";
import {BreadCrumbV2} from "../../../components/breadCrumb/BreadCrumbV2";


export const ProjectCreatePage: React.FC = (props: any) => {
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
        }
        ).catch((error) => {
            console.log(error);
            setToastStatus({ type: "error", message: "Snap! There was an error. Please check your crendentials" });
        });
    }

    const onSubmit = (data: any) => {
        console.log("on_submit:", data);
        createNewProject(data);
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
                onSubmit={onSubmit} />
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

    const Nav = [
        { name: "projects", url: "/projects", label: "Projects", index: 0 },
        { name: "project", url: "", index: 1, label: 'Create' },
    ]


    return (
        <div className="py-4 px-16">
            <ErrorBoundary>
                <div className="mb-6"><BreadCrumbV2 items={Nav} /></div>
                {launchForm()}
                {toast()}
            </ErrorBoundary>
        </div>
    );
}

export default ProjectCreatePage;
