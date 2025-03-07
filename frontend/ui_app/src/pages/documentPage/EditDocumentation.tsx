import React, { useState } from "react";
import styles from "./documentation.module.scss";
import { Button, Modal } from "react-bootstrap";
import { MarkdownEditor } from "../../components/markDownEditor";
import { SpinIndicator } from "../../components/spinIndicator";

interface Props {
    doc: string | null,
    onSave: Function;
    onCancel: Function;
    show: boolean;
}

enum REQUEST_STATUS {
    NOT_STARTED = 0,
    STARTED,
    COMPLETED
}

export default function EditDocumentation(props: Props) {
    const [requestStatus, setRequestStatus] = useState(REQUEST_STATUS.NOT_STARTED);

    const onCancel = (e: any) => {
        console.log("on hide called: ", e);
        props.onCancel();
    }

    let docChanges: any = { text: null, didChange: false };

    const onSave = (e: any) => {
        //save to asset_server
        updateDocumentation(props.onSave, props.onCancel);
    }

    const onReadmeContentChanged = (text: string) => {
        docChanges.didChange = true;
        docChanges.text = text;
        // console.log(docChanges.text);
    }

    return (
        <Modal className={styles.readmeModal} show={props.show} onHide={onCancel as any}>
            <Modal.Header>
                <div className={styles.headerContent}>
                    <Button variant="secondary" onClick={onCancel}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary"
                        // TODO: RESTRICTED TO ADMIN ONLY
                        disabled={true}
                        onClick={onSave}>
                        Save Changes
                    </Button>
                </div>
            </Modal.Header>
            <Modal.Body>
                <MarkdownEditor onChange={onReadmeContentChanged}
                    mdContent={props.doc!}
                    showTabs={true}
                    mode={"edit"} />
            </Modal.Body>
            {requestStatus === REQUEST_STATUS.STARTED && <SpinIndicator message={"Updating..."} />}
        </Modal>
    );

    function updateDocumentation(onSave: Function, onCancel: Function) {
        if (!docChanges.didChange || docChanges.text === props.doc) {
            onCancel()
        } else {
            // TODO: UPDATE DOC
            onSave("success");
        }
    }

}