import React, {useEffect} from "react";
import {useQuery} from "../../utils/utils";
import DisplayAssetClass from "./DisplayAssetClass";
import CreateAssetClass from "./CreateAssetClass";

export default function AssetClassPage() {
    const query = useQuery();
    console.log(query)
    const class_name = query.get("name");
    const action: string = query.get("action") || "display";
    const project_id: string = query.get("project_id")

    useEffect(() => {
        window.scrollTo(0, 0)
    }, []);

    return (
        <div className='p-4'>
            <div>
                {(class_name && action === "display") ? <DisplayAssetClass project_id={project_id}/> : null}
                {(action === "create") ? <CreateAssetClass project_id={project_id}/> : null}
            </div>
        </div>
    )
}
