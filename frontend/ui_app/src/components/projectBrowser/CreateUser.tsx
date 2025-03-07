import React, { useState } from "react";
import styles from "./create_user.module.scss";
import { StoreNames, useStore } from "../../stores";
import { Button, Modal, Form, Col } from "react-bootstrap";
import { Project } from "../../servers/asset_server";
import { AlertDismissible } from "../alerts";

interface Props {
    show: boolean;
    setShow: Function;
    project: Project;
    onSubmit: Function;
}

export default function CreateUser(props: Props) {
    const userStore = useStore(StoreNames.userStore);
    const [username, setUsername] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [message, setMessage] = useState<string>('');
    const [error, setError] = useState<string>('');

    const handleClick = () => {
        Project.addUser(userStore.get('user').username, username, email, props.project.name)
            .then((data: any) => {
                setMessage("Success")
                props.onSubmit();
                props.setShow(false);
            }).catch((error: any) => {
                setError(`On Snap there is an error! 
            Please make sure this user has signed up and 
            you have entered the correct username/email.
            Other than that, please contact the project owner.`)
            })
    }

    // TODO: ADD A SUCCESS TOAST
    return (
        <div>
            <Modal show={props.show} centered>
                <div>
                    <div className={styles.cardHeader}>
                        {"Add User to Current Project"}
                    </div>
                    <Modal.Body>
                        <div className={styles.body}>
                            <Form.Group as={Col} md="12" controlId="username" className={styles.pathField}>
                                <Form.Label className={styles.fieldLabel}>Enter Unix ID: </Form.Label>
                                <Form.Control
                                    required
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value.trim().toLowerCase())}
                                />
                                <Form.Label className={styles.fieldLabel}>Enter Email: </Form.Label>
                                <Form.Control
                                    required
                                    type="text"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value.trim().toLowerCase())}
                                />
                            </Form.Group>
                            {message && <AlertDismissible variant={"success"}>{message}</AlertDismissible>}
                            {error && <AlertDismissible>{error}</AlertDismissible>}
                        </div>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary"
                            style={{ marginRight: 10 }} onClick={() => props.setShow(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" variant={"primary"} onClick={() => handleClick()}>
                            {"Create"}
                        </Button>
                    </Modal.Footer>
                </div>
            </Modal>
        </div>
    );
}