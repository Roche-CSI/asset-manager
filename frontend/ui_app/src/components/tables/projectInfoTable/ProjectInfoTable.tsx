import React from "react";
import styles from "./projectinfo_table.module.scss";
import { PagedTable } from '../pagedTable';
import { Project } from "../../../servers/asset_server";
import { jsonPretty } from "../../../utils/utils";
import { CodeEditor } from "../../codeEditor";

const tableHeading = [
    'Settings',
    'Value',
]

const renderHead = (item: any, index: number) => {
    return (
        <th key={index}>
            {item}
        </th>
    );
};

const renderBody = (setting: any, index: number) => {
    return (
        <tr key={index}>
            <td>{setting.setting}</td>
            <td>{
                typeof setting.value === "object" ?
                    <CodeEditor
                        className={`${styles.yamlContainer} `}
                        height={250}
                        language={"yaml"}
                        value={jsonPretty(setting.value)}
                        readonly={true}
                        lineNumbers={false}
                        minimap={false}
                    />
                    : String(setting.value)
            }</td>
        </tr>
    )
}


interface TableProps {
    project: Project;
}

export default function ProjectInfoTable(props: TableProps) {
    const proj: Project = props.project;

    // TODO: show credentials to admin only
    const settings: any = [
        { setting: "created_by", value: proj.created_by },
        { setting: "description", value: proj.description },
        { setting: "is_active", value: proj.is_active },
        { setting: "remote_url", value: proj.remote_url },
        { setting: "staging_url", value: proj.staging_url },
        // { setting: "credentials_server", value: proj.credentials_server },
        // { setting: "credentials_user", value: proj.credentials_user }
    ]

    return (
        <>
            <PagedTable
                limit='10'
                headData={tableHeading}
                renderHead={(item: any, index: number) => renderHead(item, index)}
                bodyData={settings}
                renderBody={(item: any, index: number) => renderBody(item, index)}
                styles={styles}
            />
        </>
    )
}