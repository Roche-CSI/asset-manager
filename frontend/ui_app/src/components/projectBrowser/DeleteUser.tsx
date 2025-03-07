import React, { useState } from "react";
import styles from "./create_user.module.scss";
import { StoreNames, useStore } from "../../stores";
import { Button, Modal, Form, Col } from "react-bootstrap";
import Project, { UserRole } from "../../servers/asset_server/project";
import { AlertDismissible } from "../alerts";

interface Props {
    show: boolean;
    setShow: Function;
    project: Project;
    userRole: UserRole;
    onSubmit: Function;
}

export default function DeleteUser(props: Props) {
    const userStore = useStore(StoreNames.userStore);
    const [message, setMessage] = useState<string>('');
    const [error, setError] = useState<string>('');

    const handleClick = () => {
        Project.deleteUser(props.userRole.id, userStore.get('user').username, props.project.name)
            .then((data: any) => {
                setMessage("Success")
                props.onSubmit();
                props.setShow(false);
            }).catch((error: any) => {
                setError(`On Snap! You are not an admin of this project. Please contact the project owner.`)
            })
    }

    // TODO: ADD A SUCCESS TOAST
    return (
        <div>
            <Modal show={props.show} centered>
                <div>
                    <div className={styles.cardHeader}>
                        {"Delete"}
                    </div>
                    <Modal.Body>
                        <div className={styles.body}>
                            <div>
                                <span>Are you sure you want to remove</span>
                                <span className={styles.username}>{props.userRole.username}</span>
                                <span>from this project?</span>
                            </div>
                            {message && <AlertDismissible variant={"success"}>{message}</AlertDismissible>}
                            {error && <AlertDismissible>{error}</AlertDismissible>}
                        </div>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="primary"
                            style={{ marginRight: 10 }} onClick={() => props.setShow(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" variant={"secondary"} onClick={() => handleClick()}>
                            {"Remove"}
                        </Button>
                    </Modal.Footer>
                </div>
            </Modal>
        </div>
    );
}