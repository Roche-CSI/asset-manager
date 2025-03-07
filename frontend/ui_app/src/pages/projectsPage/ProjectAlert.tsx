import React from "react";
import styles from "./project_alert.module.scss";
import { Button, Modal } from "react-bootstrap";
import { StoreNames, useStore } from "../../stores";

interface Props {
    show: boolean;
    setShow: Function;
    projects: any[];
}

export default function ProjectAlert(props: Props) {
    const userStore = useStore(StoreNames.userStore);
    const active_project: string = userStore.get("active_project")
    const defaultProject: any = userStore.get("projects")?.[active_project];

    const handleClick = () => {
        props.setShow(false);
    }

    return (
        <div>
            <Modal show={props.show} size="lg" centered>
                <div>
                    <div className={styles.cardHeader}>
                        {"Note"}
                    </div>
                    <Modal.Body>
                        <div className={styles.body}>
                            <div>
                                <span className={styles.projectName}>Your current default project is: </span>
                                <span className={styles.highlight}>{defaultProject.description}</span>
                            </div>
                            <div>
                                <span>Here is a list of all projects:</span>
                            </div>
                            <div className={styles.prjectList}>
                                {props.projects.map((proj: any, idx: number) => (
                                    <div className={styles.prjectListItem} key={proj.id}>
                                        <span className={styles.projectName}>{`${proj.description} - `}</span>
                                        <span>Admin Id:</span>
                                        <span>{proj.created_by}</span>
                                    </div>
                                ))}
                            </div>
                            <div>
                                <span>Please get in touch with the admin if you would like access to other projects.</span>
                            </div>
                        </div>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button type="submit" variant="primary" onClick={() => handleClick()}>
                            Continue
                        </Button>
                    </Modal.Footer>
                </div>
            </Modal>
        </div>
    );
}