import React, { useEffect, useState } from "react";
import styles from "./browser.module.scss";
import { convertToCurrentTimeZone } from "../../utils";
import { StoreNames, useStore } from "../../stores";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import PersonAddAltIcon from '@mui/icons-material/PersonAddAlt';
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined';
import CloseIcon from '@mui/icons-material/Close';
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import { Col, Row } from "react-bootstrap";
import IconButton from "@mui/material/IconButton";
import FormatListBulletedOutlinedIcon from '@mui/icons-material/FormatListBulletedOutlined';
import ModeEditOutlineOutlinedIcon from '@mui/icons-material/ModeEditOutlineOutlined';
import StickyNote2OutlinedIcon from '@mui/icons-material/StickyNote2Outlined';
import { MarkdownEditor } from "../markDownEditor";
import Project, { UserRole } from "../../servers/asset_server/project";
import { ProjectInfoTable } from "../tables/projectInfoTable";
import CreateUser from "./CreateUser";
import DeleteUser from "./DeleteUser";
import ProjectLauncher from "../../pages/projectsPage/ProjectLauncher";

interface BrowserProps {
    project: any;
    iconMap: any;
}

export default function ProjectBrowser(props: BrowserProps) {
    // states
    const [project, setProject] = useState<Project>(props.project);
    const [editProject, seteditProject] = useState<boolean>(false);
    const [addUser, setAddUser] = useState<boolean>(false);
    const [deleteUser, setDeleteUser] = useState<boolean>(false);
    const [projectUsers, setProjectUsers] = useState<UserRole[]>([]);
    // stores
    const userStore = useStore(StoreNames.userStore);
    const projectStore = useStore(StoreNames.projectStore);
    const isAdmin: boolean = userStore.get("projects")?.[props.project?.id]?.can_admin_project;

    useEffect(() => {
        fetchProjectUsers();
    }, [project])


    const onUpdate = () => {
        setProject(projectStore.get(project.id))
        seteditProject(false)
    }

    if (!project) {
        return null;
    }

    const fetchProjectUsers = () => {
        if (project) {
            Project.getUsersList(userStore.get("user").username, project.name)
                .then((data: any[]) => {
                    setProjectUsers(data)
                }).catch((error: any) => {
                    console.error(error)
                })
        }
    }

    const header = (project: Project) => {
        return (
            <div className={styles.cardHeader}>
                <div className={styles.headerItem}>
                    <AccountCircleIcon />
                    <span style={{ fontWeight: "bold" }}>{project.created_by}</span>
                    <ArticleOutlinedIcon />
                    <span>{project.name}</span>
                    <StickyNote2OutlinedIcon />
                    <span>{project.id}</span>
                    <AccessTimeIcon />
                    <span>{convertToCurrentTimeZone(project.created_at, "date")}</span>
                </div>
                <div className={styles.headerItem}>
                    {isAdmin &&
                        <IconButton onClick={(e: any) => seteditProject(true)}>
                            <ModeEditOutlineOutlinedIcon />
                        </IconButton>
                    }
                </div>
            </div>
        )
    }

    return (
        <div className={`${styles.page}`}>
            <Row style={{ width: "100%" }}>
                <Col md={8}>
                    <div className={`${styles.card}`}>
                        {header(project)}
                        {project && <ProjectInfoTable project={project} />}
                    </div>
                </Col>
                <Col md={4}>
                    <div className={`${styles.card}`}>
                        <div className={styles.textBox}>
                            <div className={styles.textBoxHeader}>
                                <div className={styles.tbHeaderContents}>
                                    <div className={styles.textBoxHeaderItem}>
                                        <h5>
                                            {project.name}
                                        </h5>
                                    </div>
                                    {isAdmin &&
                                        <div className={styles.textBoxHeaderIcon} onClick={() => setAddUser(true)}>
                                            <span>Add User</span>
                                            <PersonAddAltIcon />
                                        </div>
                                    }
                                </div>
                            </div>
                            <div className={styles.textBoxBody}>
                                <div>
                                    <h6>Project members</h6>
                                    <div className={styles.userList}>
                                        {projectUsers.map((userRole: any, idx: number) => (
                                            <div className={styles.userListItem} key={idx} >
                                                <div>
                                                    <AccountCircleIcon />
                                                    {userRole.username}
                                                </div>
                                                {isAdmin &&
                                                    <div>
                                                        <CloseIcon className={styles.userListIcon} onClick={() => setDeleteUser(true)} />
                                                        {deleteUser && <DeleteUser show={deleteUser} setShow={setDeleteUser}
                                                            userRole={userRole} onSubmit={fetchProjectUsers} project={props.project} />}
                                                    </div>
                                                }
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </Col>
                <Col md={12}>
                    <div className={styles.card}>
                        <div className={styles.textBoxHeader}>
                            <div className={styles.tbHeaderContents}>
                                <div className={styles.readMeContainer}>
                                    <FormatListBulletedOutlinedIcon />
                                    <span>README.md</span>
                                </div>
                            </div>
                        </div>
                        <div>
                            <MarkdownEditor mode={"preview"}
                                showTabs={false}
                                mdContent={project ? project.readme : ""} />
                        </div>
                    </div>
                </Col>
            </Row>
            {addUser && <CreateUser show={addUser} setShow={setAddUser}
                project={props.project} onSubmit={fetchProjectUsers} />}
            {editProject &&
                <ProjectLauncher
                    onLaunch={onUpdate}
                    onCancel={() => seteditProject(false)}
                    project={project}
                    type={"edit"} />
            }
        </div >
    )
}

