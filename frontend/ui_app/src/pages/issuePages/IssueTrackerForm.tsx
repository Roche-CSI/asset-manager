import React, { useEffect, useState } from "react";
import styles from "./issue.module.scss";
import { Form, Col, Row, Button, Alert } from "react-bootstrap";
import { ErrorBoundary } from "../../components/errorBoundary";

export const repos = [
    { value: 'asset_client', label: 'Command Line Interface' },
    { value: 'asset_dashboard', label: 'Dashboard UI' },
]

interface Props {
    onSubmit: Function;
    onFieldChanged: Function;
    title: string;
    description: string;
    repo_name: string;
    validated: boolean;
    errors?: any;
}

export default function IssueTrackerForm(props: Props) {
    const [formErrors, setFormErrors] = useState<any>({});
    const [validated, setValidated] = useState(false);
    useEffect(() => {
        setFormErrors((formErrors: any) => ({ ...props.errors }));
        setValidated(props.validated);
    }, [props.errors, props.validated])

    function onSubmit(event: any) {
        const form = event.currentTarget;
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
            setValidated(true);
        } else {
            props.onSubmit(event);
        }
    }

    return (
        <Form noValidate
            validated={validated}
            onSubmit={onSubmit}
            className={styles.form}>
            <Row className="mb-6">
                <Form.Group as={Col} md="20" controlId="validationCustom01" className={styles.formField}>
                    <Form.Label>Title</Form.Label>
                    <Form.Control
                        required
                        isInvalid={!!formErrors.title}
                        type="text"
                        placeholder="Enter Summary"
                        value={props.title}
                        onChange={(e) => props.onFieldChanged(e, "title")}
                    />
                    <Form.Control.Feedback
                        type="invalid">{formErrors.title || 'Enter title'}</Form.Control.Feedback>
                </Form.Group>
                <Form.Group as={Col} md="20" controlId="validationCustom03" className={styles.formField}>
                    <Form.Label>Asset Manager Tool</Form.Label> 
                    <Form.Select aria-label="Default select example"
                        required
                        value={props.repo_name}
                        isInvalid={!!formErrors.repo_name}
                        onChange={(e) => props.onFieldChanged(e, "repo_name")}>
                        {
                            repos.map((repo: any, index: number) => {
                                return <option key={index} value={repo.value}>{repo.label}</option>
                            })
                        }
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">{formErrors.repo_name}</Form.Control.Feedback>
                </Form.Group>
            </Row>
            <Row className="mb-3">
                <Form.Group as={Col} md="14" controlId="validationCustom03" className={styles.formField}>
                    <Form.Label>Description</Form.Label>
                    <Form.Control
                        placeholder="Enter Issue Description"
                        required as="textarea"
                        rows={10}
                        onChange={(e) => props.onFieldChanged(e, "description")}
                    />
                    <Form.Control.Feedback
                        type="invalid">{formErrors.description || "Enter description"}</Form.Control.Feedback>
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
            <Row className="mb-3">
                <Col md={"12"} className="flex justify-center items-center">
                    <Button type="submit">Submit</Button>
                </Col>
            </Row>
        </Form>
    );

    function unKnownError(error: any) {
        console.log("error:", error);
        return (
            <ErrorBoundary>
                <div>
                    <Alert show={true} variant="danger">
                        <Alert.Heading>Error</Alert.Heading>
                    </Alert>
                </div>
            </ErrorBoundary>
        )
    }
}
