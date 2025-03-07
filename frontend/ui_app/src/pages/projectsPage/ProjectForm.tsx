import React, { useEffect, useState } from "react";
import { Alert, Button, Col, Form, Modal, Row } from "react-bootstrap";
import { ProjectFormData, ProjectFormErrors } from "./formControls";
import styles from "./launcher.module.scss";
import {CodeEditor} from "../../components/codeEditor";
import { CloseOutlined } from "@mui/icons-material";
import IconButton from "@mui/material/IconButton";
import { jsonPretty } from "../../utils/utils";
import { validateJSON } from "../../utils";
import { isEmptyObject } from "../../utils/utils";

export interface DisplayInfo {
    description: string;
    readonly?: boolean;
    retry?: boolean;
}

interface Props {
    formData: ProjectFormData;
    displayInfo: DisplayInfo;
    onSubmit?: Function;
    onCancel?: Function;
}

export default function ProjectForm(props: Props) {
    const defaultFormData = {
        name: props.formData.name || '',
        description: props.formData.description || '',
        is_active: props.formData.is_active || true,
        staging_url: props.formData.staging_url || '',
        remote_url: props.formData.remote_url || '',
        credentials_user: props.formData.credentials_user || 
            {"__hint__": "This is add and read permission to the bucket"},
        credentials_server: props.formData.credentials_server || 
            {"__hint__": "This is all permission to the bucket"},
        readme: props.formData.readme || '',
        user: props.formData.user || '',
        modified_by: props.formData.modified_by || '',
    }
    // states
    const [validated, setValidated] = useState(false);
    const [formErrors, setFormErrors] = useState<ProjectFormErrors>({});
    const [formData, setFormData] = useState<ProjectFormData>(defaultFormData);

    const validateForm = (form: any) => {
        let form_valid = form.checkValidity();
        const errors: any = {};
        // make a copy of formData, so we can do conditional validation
        const data: any = {};
        const [valid_credentials_user, credentials_user_error] = validateJSON(JSON.stringify(formData.credentials_user));
        if (!valid_credentials_user) {
            form_valid = false;
            errors.credentials_user = credentials_user_error;
        }
        const [valid_credentials_server, credentials_server_error] = validateJSON(JSON.stringify(formData.credentials_server));
        if (!valid_credentials_server) {
            form_valid = false;
            errors.credentials_server = credentials_server_error;
        }
        return [Boolean(form_valid && isEmptyObject(errors)), errors, {...formData, ...data}];
    }

    const onSubmit = (event: any) => {
        event.preventDefault();
        event.stopPropagation();
        const form = event.currentTarget;
        setValidated(true);
        const [valid, errors, data] = validateForm(form)
        if (valid) {
            setFormErrors(errors);
            console.log("data is: ", data)
            props.onSubmit && props.onSubmit(data);
        }else {
            setFormErrors(errors);
        }
    }

    const onFieldChanged = (event: any,
        fieldName: string,
        type: string = "text"
    ) => {
        let content: any;
        if (type === "checkbox") {
            content = event.target.checked;
        } else if (type === "object") {
            content = JSON.parse(event)
        } else {
            content = (typeof event === "string") ? event : event.target.value;
        }
        setFormData((formData) => {
            return { ...formData, [fieldName]: content }
        })
    }

    console.log("formData: ", formData, ", formErrors: ", formErrors);
    const displayInfo = props.displayInfo;
    const fieldGroupCSS = `${styles.fieldGroup} ${displayInfo.readonly ? styles.readonly : ""}`;
    return (
        <React.Fragment>
            <Form noValidate
                validated={validated}
                className={styles.form}
                onSubmit={onSubmit}>
                {formHeader()}
                <Modal.Body>
                    <div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{name()}</Row>
                        </div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{description()}</Row>
                        </div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{isActive()}</Row>
                        </div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{remoteURL()}</Row>
                        </div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{credentialsUser()}</Row>
                        </div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{credentialsServer()}</Row>
                        </div>
                        <div className={fieldGroupCSS}>
                            <Row className="mb-3">{readme()}</Row>
                        </div>
                        <Row className="mb-3">{userFields()}</Row>
                    </div>
                    {
                        formErrors.unknown &&
                        <Row className="mb3">
                            <Form.Group as={Col} md={"11"} className={styles.formField}>
                                {unKnownError(formErrors.unknown)}
                            </Form.Group>
                        </Row>
                    }
                </Modal.Body>
                {formButtons()}
            </Form>
        </React.Fragment>
    );

    function formHeader() {
        if (displayInfo.readonly) return null;
        return (
            <Modal.Header>
                <div className={styles.header}>
                    <div className={styles.cardHeader}>
                        <div><h3>{displayInfo.description}</h3></div>
                        <div className={styles.buttonContainer}>
                            <IconButton onClick={(e) => props.onCancel && props.onCancel()}>
                                <CloseOutlined />
                            </IconButton>
                        </div>
                    </div>
                </div>
            </Modal.Header>
        )
    }

    function formButtons() {
        if (displayInfo.readonly) return null;
        return (
            <Modal.Footer>
                <Button variant="secondary"
                    style={{ marginRight: 10 }}
                    onClick={(e) => props.onCancel && props.onCancel()}>
                    Cancel
                </Button>
                <Button type="submit" variant={displayInfo.retry ? "danger" : "primary"}>
                    {displayInfo.retry ? "Try again" : "Create"}
                </Button>
            </Modal.Footer>
        )
    }

    function name() {
        return (
            <>
                <Form.Group as={Col} md="4" controlId="name" className={styles.pathField}>
                    <Form.Label className={styles.fieldLabel}>Name</Form.Label>
                    <Form.Control
                        readOnly={Boolean(displayInfo.readonly)}
                        isInvalid={Boolean(formErrors.name)}
                        required={true}
                        type="text"
                        placeholder="Enter Project Name"
                        value={formData.name}
                        onChange={(e) => onFieldChanged(e.target.value, "name", "string")}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.name ? styles.invalid : styles.valid}`}>
                            {formErrors.name}
                        </div>
                    }
                </Form.Group>
            </>
        )
    }

    function description() {
        return (
            <>
                <Form.Group as={Col} md="4" controlId="description" className={styles.pathField}>
                    <Form.Label className={styles.fieldLabel}>Description</Form.Label>
                    <Form.Control
                        readOnly={Boolean(displayInfo.readonly)}
                        isInvalid={Boolean(formErrors.description)}
                        required
                        type="text"
                        placeholder="Enter Description"
                        value={formData.description}
                        onChange={(e) => onFieldChanged(e.target.value, "description", "string")}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.description ? styles.invalid : styles.valid}`}>
                            {formErrors.description}
                        </div>
                    }
                </Form.Group>
            </>
        )
    }

    function isActive() {
        return (
            <>
                <Form.Group as={Col} md="12" controlId="is_active" className={styles.formField}>
                    <Form.Label className={styles.fieldLabel}>Is Active</Form.Label>
                    <Form.Check
                        className={styles.checkBox}
                        aria-label="is_active"
                        disabled={Boolean(displayInfo.readonly)}
                        isInvalid={Boolean(formErrors.is_active)}
                        checked={formData.is_active}
                        type="checkbox"
                        onChange={(e) =>
                            onFieldChanged(e, "is_active", "checkbox")}
                    />
                </Form.Group>
            </>
        )
    }

    function stagingURL() {
        return (
            <>
                <Form.Group as={Col} md="12" controlId="staging_url" className={styles.formField}>
                    <Form.Label className={styles.fieldLabel}>Staging URL</Form.Label>
                    <Form.Control
                        readOnly={Boolean(displayInfo.readonly)}
                        isInvalid={Boolean(formErrors.staging_url)}
                        required
                        type="text"
                        value={formData.staging_url}
                        onChange={(e) => onFieldChanged(e.target.value, "staging_url", "string")}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.staging_url ? styles.invalid : styles.valid}`}>
                            {formErrors.staging_url}
                        </div>
                    }
                </Form.Group>
            </>
        )
    }

    function remoteURL() {
        return (
            <>
                <Form.Group as={Col} md="12" controlId="remote_url" className={styles.formField}>
                    <Form.Label className={styles.fieldLabel}>Remote URL</Form.Label>
                    <Form.Control
                        readOnly={Boolean(displayInfo.readonly)}
                        isInvalid={Boolean(formErrors.remote_url)}
                        required={true}
                        type="text"
                        value={formData.remote_url}
                        onChange={(e) => onFieldChanged(e.target.value, "remote_url", "string")}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.remote_url ? styles.invalid : styles.valid}`}>
                            {formErrors.remote_url}
                        </div>
                    }
                </Form.Group>
            </>
        )
    }

    function credentialsUser() {
        return (
            <React.Fragment>
                <Form.Group as={Col} md="12" controlId="credentials_user" className={styles.formField}>
                    <Form.Label className={styles.fieldLabel}>Credentials User</Form.Label>
                    <CodeEditor
                        className={`${styles.yamlContainer} 
                                    ${validated ? formErrors.credentials_user ? styles.invalid : styles.valid : ""}`}
                        height={200}
                        language={"json"}
                        value={jsonPretty(formData.credentials_user)}
                        onChange={(text: string) => onFieldChanged(text, "credentials_user", "object")}
                        readonly={Boolean(displayInfo.readonly)}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.credentials_user ? styles.invalid : styles.valid}`}>
                            {formErrors.credentials_user || "Looks good"}
                        </div>
                    }
                </Form.Group>
            </React.Fragment>
        )
    }

    function credentialsServer() {
        return (
            <React.Fragment>
                <Form.Group as={Col} md="12" controlId="credentials_server" className={styles.formField}>
                    <Form.Label className={styles.fieldLabel}>Credentials Server</Form.Label>
                    <CodeEditor
                        className={`${styles.yamlContainer} 
                                    ${validated ? formErrors.credentials_server ? styles.invalid : styles.valid : ""}`}
                        height={200}
                        language={"json"}
                        value={jsonPretty(formData.credentials_server)}
                        onChange={(text: string) => onFieldChanged(text, "credentials_server", "object")}
                        readonly={Boolean(displayInfo.readonly)}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.credentials_server ? styles.invalid : styles.valid}`}>
                            {formErrors.credentials_server || "Looks good"}
                        </div>
                    }
                </Form.Group>
            </React.Fragment>
        )
    }

    function readme() {
        return (
            <React.Fragment>
                <Form.Group as={Col} md="12" controlId="readme" className={styles.formField}>
                    <Form.Label className={styles.fieldLabel}>Readme</Form.Label>
                    <CodeEditor
                        className={`${styles.yamlContainer} 
                                    ${validated ? formErrors.readme ? styles.invalid : styles.valid : ""}`}
                        height={200}
                        language={"txt"}
                        value={formData.readme}
                        onChange={(text: string) => onFieldChanged(text, "readme")}
                        readonly={Boolean(displayInfo.readonly)}
                    />
                    {
                        validated &&
                        <div
                            className={`${styles.feedback} ${formErrors.readme ? styles.invalid : styles.valid}`}>
                            {formErrors.readme || "Looks good"}
                        </div>
                    }
                </Form.Group>
            </React.Fragment>
        )
    }

    function userFields() {
        return (
            <React.Fragment>
                <Form.Group as={Col} md="4" controlId="validationCustom03" className={styles.formField}>
                    <Form.Label>Created By</Form.Label>
                    <Form.Control
                        readOnly={Boolean(displayInfo.readonly)}
                        isInvalid={!!formErrors.user}
                        disabled={true}
                        required
                        type="text"
                        value={formData.user}
                        onChange={(e) => onFieldChanged(e, "user")}
                    />
                    <Form.Control.Feedback type="invalid">{formErrors.user}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="4" controlId="validationCustom02" className={styles.formField}>
                    <Form.Label>Modified By</Form.Label>
                    <Form.Control
                        readOnly={Boolean(displayInfo.readonly)}
                        isInvalid={!!formErrors.modified_by}
                        disabled={true}
                        required
                        type="text"
                        value={formData.modified_by}
                        onChange={(e) => onFieldChanged(e, "modified_by")}
                    />
                    <Form.Control.Feedback type="invalid">{formErrors.modified_by}</Form.Control.Feedback>
                </Form.Group>
            </React.Fragment>
        )
    }

    function unKnownError(error: any) {
        console.log("error:", error);
        return (
            <div>
                <Alert show={true} variant="danger">
                    <Alert.Heading>Error</Alert.Heading>
                </Alert>
            </div>
        )
    }
}