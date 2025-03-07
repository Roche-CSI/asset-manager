import React, { useEffect, useRef, useState } from "react";
import "./form_template.css"
import { Form, Col, Row, InputGroup, Button, Alert } from "react-bootstrap";
import { MarkdownEditor } from "../../components/markDownEditor";
import { ErrorBoundary } from "../../components/errorBoundary";

const CLASS_TYPE = {
    NONE: "",
    DOCKER: "docker",
    GENERAL: "general",
    IMAGES: "images",
    MODELS: "models"
}

interface Props {
    onSubmit: Function;
    onFieldChanged: Function;
    title: string;
    description: string;
    class_type: string;
    name: string;
    has_readme: boolean;
    project_id: string;
    project_name: string;
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
        setFormErrors((formErrors: any) => ({ ...props.errors }));
        setValidated(props.validated);
    }, [props.errors, props.validated, props.has_readme])

    function onReadMeChange(val: string) {
        props.onFieldChanged && props.onFieldChanged(val, "readme");
    }

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
        <div className='form-container'>
            {/* <!-- Contact Form --> */}
            {formHeader()}
            <Form noValidate
                validated={validated}
                onSubmit={onSubmit}
            >
                <div className='p-6.5'>
                    <Row className='row-container'>
                        <Form.Group controlId="validationCustom01" className='form-group'>
                            <Form.Label className='form-label'>Asset Class Title {requiredIcon()}</Form.Label>
                            <Form.Control
                                className='form-input'
                                required
                                isInvalid={!!formErrors.title}
                                type="text"
                                placeholder="Enter asset class title"
                                value={props.title}
                                onChange={(e) => props.onFieldChanged(e, "title")}
                            />
                            <Form.Control.Feedback
                                type="invalid">{formErrors.title}</Form.Control.Feedback>
                        </Form.Group>
                        <Form.Group controlId="validationCustom03" className='form-group'>
                        <Form.Label className='form-label'>Type</Form.Label>
                            <div className='form-select-container'>
                                <Form.Select aria-label="Default select example"
                                    className='form-select'
                                    required
                                    isInvalid={!!formErrors.class_type}
                                    onChange={(e) => props.onFieldChanged(e, "class_type")}>
                                    {
                                        Object.values(CLASS_TYPE).map(
                                            (val: string, index: number) => <option key={index} value={val}>{val}</option>)
                                    }
                                </Form.Select>
                            </div>
                            <Form.Control.Feedback type="invalid">{formErrors.class_type}</Form.Control.Feedback>
                        </Form.Group>
                        <Form.Group as={Col} controlId="validationCustom02" className='form-group'>
                            <Form.Label className='form-label'>Asset Class Name {requiredIcon()}</Form.Label>
                            <Form.Control
                                className='form-input'
                                isInvalid={!!formErrors.name}
                                required
                                type="text"
                                placeholder="Enter class_id"
                                value={props.name}
                                onChange={(e) => props.onFieldChanged(e, "name")}
                            />
                            <Form.Control.Feedback
                                type="invalid">{formErrors.name}</Form.Control.Feedback>
                        </Form.Group>
                    </Row>
                    <Row className='row-container'>
                        <Form.Group controlId="validationCustom03" className='form-group'>
                            <Form.Label className='form-label'>Description {requiredIcon()}</Form.Label>
                            <Form.Control
                                className='form-textarea'
                                placeholder="Enter description"
                                required
                                as="textarea"
                                rows={6}
                                onChange={(e) => props.onFieldChanged(e, "description")}
                            />
                            <Form.Control.Feedback
                                type="invalid">{formErrors.description}</Form.Control.Feedback>
                        </Form.Group>
                    </Row>
                    <Row className='row-container'>
                        <Form.Group controlId="validationCustom02" className='form-group'>
                            <Form.Label className='form-label'>Project ID</Form.Label>
                            <Form.Control
                                className='form-input'
                                readOnly={true}
                                isInvalid={!!formErrors.project_id}
                                required
                                type="text"
                                placeholder="project_id"
                                value={props.project_id}
                            />
                            {/* <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback> */}
                            <Form.Control.Feedback
                                type="invalid">{formErrors.project_id}</Form.Control.Feedback>
                        </Form.Group>
                        <Form.Group controlId="validationCustom02" className='form-group'>
                            <Form.Label className='form-label'>Project Name</Form.Label>
                            <Form.Control
                                className='form-input'
                                readOnly={true}
                                isInvalid={!!formErrors.project_name}
                                type="text"
                                placeholder="project_name"
                                value={props.project_name}
                            />
                            {/* <Form.Control.Feedback type="valid">Looks good!</Form.Control.Feedback> */}
                            <Form.Control.Feedback
                                type="invalid">{formErrors.project_name}</Form.Control.Feedback>
                        </Form.Group>
                    </Row>
                    {/*<Row className="mb-3">*/}
                    {/*    <Form.Group as={Col} md={"12"} className={styles.formField}>*/}
                    {/*        <Form.Check label="add a README.md file" onChange={(e) => props.onFieldChanged(e, "has_readme")}/>*/}
                    {/*        {props.has_readme && readMeEditor(onReadMeChange)}*/}
                    {/*    </Form.Group>*/}
                    {/*</Row>*/}
                    {
                        formErrors.unknown &&
                        <Row className="mb3">
                            <Form.Group as={Col} md={"11"} className='form-group'>
                                {unKnownError(formErrors.unknown)}
                            </Form.Group>
                        </Row>
                    }
                    <Row className="mb-3">
                        <Col md={"12"}>
                            <Button type="submit" className='form-button'>Create</Button>
                        </Col>
                    </Row>
                </div>
            </Form>
        </div>
    );

    function formHeader() {
        return (
            <div className='border-b border-stroke px-6.5 py-4 dark:border-strokedark'>
                <h3 className='font-medium text-black dark:text-white'>
                    Class Form
                </h3>
            </div>
        )
    }

    function requiredIcon() {
        return <span className='text-meta-1'>*</span>
    }

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
                <Form.Group as={Col} md={"11"} className='form-group'>
                    <MarkdownEditor onChange={onChange} mode={"edit"} showTabs={false} />
                </Form.Group>
            </Row>
        )
    }
}