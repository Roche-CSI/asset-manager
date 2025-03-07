import React, {useEffect, useRef, useState} from "react";
import styles from "./edit.module.scss";
import {Form, Col, Row, InputGroup, Button, Alert, Modal} from "react-bootstrap";

import {MarkdownEditor} from "../../components/markDownEditor";
import {ErrorBoundary} from "../../components/errorBoundary";
import { CLASS_TYPE } from "../../components/assetClassBrowser";

interface Props {
    onSave: Function;
    onCancel: Function;
    onFieldChanged: Function;
    title: string;
    description: string;
    class_type: string;
    name: string;
    has_readme: boolean;
    validated: boolean;
    errors?: any;
}

/**React-Bootstrap form validation
 * https://react-bootstrap.github.io/forms/validation/
 * @constructor
 */

export default function AssetClassForm(props: Props) {

    const [formErrors, setFormErrors] = useState<any>({});
    const [validated, setValidated] = useState(false);
    useEffect(() => {
        setFormErrors((formErrors: any) => ({...props.errors}));
        setValidated(props.validated);
    }, [props.errors, props.validated, props.has_readme])

    function onReadMeChange(val: string) {
        props.onFieldChanged && props.onFieldChanged(val, "readme");
    }

    function onSubmit(event: any) {
        const form = event.currentTarget;
        // console.log("event:", event, " ,form:", form);
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
            setValidated(true);
        }else {
            props.onSave(event);
        }
    }

    function onCancel(event: any) {
        props.onCancel()
    }

    return (
        <Form noValidate
              validated={validated}
              onSubmit={onSubmit}
              className={styles.form}>
            <Row className="mb-3">
                <Form.Group as={Col} md="12" controlId="validationCustom01" className={styles.formField}>
                    <Form.Label>Asset Class Title</Form.Label>
                    <Form.Control
                        required
                        isInvalid={!!formErrors.title}
                        type="text"
                        placeholder="Asset Class Title"
                        value={props.title}
                        onChange={(e) => props.onFieldChanged(e, "title")}
                    />
                    {
                        formErrors.title ? null : <Form.Control.Feedback type="valid">{"Looks good!"}</Form.Control.Feedback>
                    }
                    <Form.Control.Feedback
                        type="invalid">{formErrors.title || 'Asset title is required'}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="12" controlId="validationCustom03" className={styles.formField}>
                    <Form.Label>Type</Form.Label>
                    <Form.Select aria-label="Default select example"
                                 required
                                 isInvalid={!!formErrors.class_type}
                                 value={props.class_type}
                                 onChange={(e) => props.onFieldChanged(e, "class_type")}>
                        {
                            Object.values(CLASS_TYPE).map(
                                (val: string, index: number) => <option key={index} value={val}>{val}</option>
                            )
                        }
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">{formErrors.class_type}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="12" controlId="validationCustom02" className={styles.formField}>
                    <Form.Label>Asset Class Id</Form.Label>
                    <Form.Control
                        readOnly={true}
                        isInvalid={!!formErrors.name}
                        required
                        type="text"
                        placeholder="class_id"
                        value={props.name}
                    />
                    <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback>
                    <Form.Control.Feedback
                        type="invalid">{formErrors.name}</Form.Control.Feedback>
                </Form.Group>
            </Row>
            <Row className="mb-3">
                <Form.Group as={Col} md="12" controlId="validationCustom03" className={styles.formField}>
                    <Form.Label>Description</Form.Label>
                    <Form.Control
                        placeholder="Description"
                        required as="textarea"
                        rows={4}
                        value={props.description}
                        onChange={(e) => props.onFieldChanged(e, "description")}
                    />
                    <Form.Control.Feedback
                        type="invalid">{formErrors.description || "Description can not be empty"}</Form.Control.Feedback>
                </Form.Group>
            </Row>
            {
                formErrors.unknown &&
                <Row className="mb3">
                    <Form.Group as={Col} md={"11"} className={styles.formField}>
                        {unKnownError(formErrors.unknown)}
                    </Form.Group>
                </Row>
            }
            <Modal.Footer>
                <Button variant="secondary" onClick={onCancel}>
                    Cancel
                </Button>
                <Button type="submit" variant="primary" onClick={onSubmit}>
                    Save Changes
                </Button>
            </Modal.Footer>
            {/*<Button type="submit">Submit</Button>*/}
        </Form>
    );

    function unKnownError(error: any) {
        console.log("error:", error);
        return (
            <ErrorBoundary>
                <div>
                    <Alert show={true} variant="danger">
                        <Alert.Heading>Error</Alert.Heading>
                        {/*<p>*/}
                        {/*    {error}*/}
                        {/*</p>*/}
                    </Alert>
                </div>
            </ErrorBoundary>
        )
    }

    function readMeEditor(onChange?: Function) {
        return (
            <Row className="mb-3">
                <Form.Group as={Col} md={"11"} className={styles.formField}>
                    <MarkdownEditor onChange={onChange}/>
                </Form.Group>
            </Row>
        )
    }
}