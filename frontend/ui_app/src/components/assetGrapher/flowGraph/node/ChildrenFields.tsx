import React from "react";
import { Link } from "react-router-dom";
import RefFields from "./RefFields";
import NodeData from "./nodeData";

interface Props {
    children: NodeData[] | null;
    project_id?: string;
}

const ChildrenFields = (props: Props) => {
    const { children, project_id } = props;

    if (!children) return;
    // sort children
    children.sort((a: any, b: any) => a.id - b.id)
    return (
        <div className="max-h-48 overflow-y-auto">
            <table>
                <tbody>
                    {children.map((child: any, index: number) => {
                        const [className, seq_id, version] = child.data.label.split("/");
                        return (
                            <tr key={`${child.data.id}, ${index}`}>
                                <td>
                                    <Link to={`/asset/${project_id}/${className}/${seq_id}/files?version=${version}`}
                                        className='text-primary text-sm'>
                                        {child.data.label}
                                    </Link>
                                    {children.length === 1 &&
                                        <RefFields assetRef={child.data.ref} />
                                    }
                                </td>
                            </tr>
                        )
                    }
                    )}
                </tbody>
            </table>
        </div>
    )
}


export default ChildrenFields;
