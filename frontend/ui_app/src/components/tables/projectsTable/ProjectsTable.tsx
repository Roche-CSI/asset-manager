import React, { Fragment, useState } from "react";
import styles from "./projects_table.module.scss";
import { PagedTable } from '../pagedTable';
import { SearchField } from "../../search";
import { Project } from "../../../servers/asset_server"
import ProjectCard from "../../../pages/projectsPage/ProjectCard";
import { ProjectIcons } from "../../../pages/projectsPage/ProjectInfoPage";
import { Col, Form } from "react-bootstrap";

const tableHeading = [
    '',
    'Details',
    'Select'
]

const renderHead = (item: any, index: number, onSearch?: Function) => {
    return (
        <th key={index}>{
            index !== 0 ? item :
                <div className={styles.titleContainer}>
                    <div className={styles.searchCard}>
                        <SearchField placeholder={"Find project..."}
                            onChange={(e: any) => onSearch && onSearch(e)} />
                    </div>
                </div>
        }</th>
    );
};


const renderBody = (p: Project, index: number, onProjectInfoClicked: Function, 
        activeProject: string, handleSelection: Function, userProjects: any) => {
    const icon: any = ProjectIcons?.[p.name] ?? ProjectIcons.default;
    const projectInfo: any[] = [{ key: "Name", val: p.name }, { key: "Description", val: p.description },
        { key: "Owner", val: p.created_by }];
    return (
        <tr key={index} className={`${activeProject === p.id? styles.active: null}`}>
            <td>
                <div className={styles.projectCard}>
                    <ProjectCard key={index}
                        icon={icon}
                        id={p.id}
                        name={p.name}
                        label={p.description}
                        onClick={onProjectInfoClicked} />
                </div>
            </td>
            <td className={styles.projectInfo}>
                {projectInfo.map((pair: any, index: number) =>
                    <div className={styles.projectInfoPair} key={index}>
                        <div className={styles.projectInfoKey}>{`${pair.key}: `}</div>
                        <div className={styles.projectInfoItem}>{pair.val}</div>
                    </div>
                )}
            </td>
            <td>
                <Form.Group as={Col} md="4" controlId="active_project" className={styles.formField}>
                    <Form.Check
                        className={styles.checkBox}
                        aria-label="checkpoints"
                        disabled={!userProjects?.[p.id]}
                        checked={activeProject === p.id}
                        type="checkbox"
                        onChange={(e) => handleSelection(p.id)}
                    />
                </Form.Group>
            </td>
        </tr>
    )
}

interface TableProps {
    projects: Project[];
    onProjectInfoClicked: Function;
    activeProject: string;
    handleSelection: Function;
    userProjects: any;
}

export default function ProjectsTable(props: TableProps) {
    let [searchKey, setSearchKey] = useState("");
    const onSearch = (val: string) => {
        // console.log(val);
        setSearchKey(val);
    }

    return (
        <Fragment>
            <PagedTable
                limit='10'
                headData={tableHeading}
                renderHead={(item: any, index: number) => renderHead(item, index, onSearch)}
                bodyData={search(props.projects, searchKey)}
                renderBody={(item: any, index: number) => 
                    renderBody(item, index, props.onProjectInfoClicked, 
                                props.activeProject, props.handleSelection, props.userProjects)}
                styles={styles}
            />
        </Fragment>
    )

    function search(data: any[], searchInput?: string) {
        if (!searchInput) {
            return data;
        }
        return data.filter(proj => String(proj.name).includes(searchInput));
    }
}