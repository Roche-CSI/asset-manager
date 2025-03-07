import React, {useEffect} from "react";
import {useQuery} from "../../utils/utils";
import {DisplayAssetClassV2} from "./DisplayAssetClassV2.tsx";
import {CreateAssetClassV2} from "./CreateAssetClassV2.tsx";

export const AssetClassPageV2: React.FC = () => {
    const query = useQuery();
    const class_name = query.get("name");
    const action: string = query.get("action") || "display";
    const project_id: string = query.get("project_id")

    useEffect(() => {
        window.scrollTo(0, 0)
    }, []);

    return (
        <React.Fragment>
            {(class_name && action === "display") ? <DisplayAssetClassV2 project_id={project_id}/> : null}
            {(action === "create") ? <CreateAssetClassV2 projectId={project_id}/> : null}
        </React.Fragment>
    )
}
