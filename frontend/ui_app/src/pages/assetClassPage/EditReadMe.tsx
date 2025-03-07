import React, {useState} from "react";
import styles from "./readme.module.scss";
import {AssetClass} from "../../servers/asset_server";
import {Button, Modal} from "react-bootstrap";
import {MarkdownEditor} from "../../components/markDownEditor";
import {StoreNames, useStore} from "../../stores";
import {SpinIndicator} from "../../components/spinIndicator";


interface Props {
    classId: string;
    readmeText: string | null,
    onSave: Function;
    onCancel: Function;
    show: boolean;
}

enum REQUEST_STATUS {
    NOT_STARTED = 0,
    STARTED,
    COMPLETED
}


export default function EditReadMe(props: Props) {
    const classIdStore = useStore(StoreNames.classIdStore);
    const classNameStore = useStore(StoreNames.classNameStore);
    const userStore = useStore(StoreNames.userStore);
    const [requestStatus, setRequestStatus] = useState(REQUEST_STATUS.NOT_STARTED);

    const onCancel = (e: any) => {
        console.log("on hide called: ", e);
        props.onCancel();
    }

    let readMeChanges: any = {text: null, didChange: false};
    const onSave = (e: any) => {
        //save to asset_server
        updateAssetClass(props.onSave, props.onCancel);
    }

    const onReadmeContentChanged = (text: string) => {
        readMeChanges.didChange = true;
        readMeChanges.text = text;
        // console.log(readMeChanges.text);
    }

    return (
        <Modal className={styles.readmeModal} show={props.show} onHide={onCancel as any}>
            <Modal.Header>
                <div className={styles.headerContent}>
                    <Button variant="secondary" onClick={onCancel}>
                        Cancel
                    </Button>
                    <Button type="submit" variant="primary" onClick={onSave}>
                        Save Changes
                    </Button>
                </div>
            </Modal.Header>
            <Modal.Body>
                <MarkdownEditor onChange={onReadmeContentChanged}
                                mdContent={props.readmeText!}
                                showTabs={true}
                                mode={"edit"}/>
            </Modal.Body>
            {requestStatus === REQUEST_STATUS.STARTED && <SpinIndicator message={"Updating..."}/>}
        </Modal>
    );

    function updateAssetClass(onSave: Function, onCancel: Function) {
        if (!readMeChanges.didChange || readMeChanges.text === props.readmeText) {
            onCancel()
        }else {
            setRequestStatus(REQUEST_STATUS.STARTED);
            AssetClass.update(props.classId, {readme: readMeChanges.text, user: userStore.get("user").username}, false).then((res) => {
                let updated = new AssetClass(res as any);
                // console.log("updated:", updated);
                classIdStore.set(updated.id, updated);
                classNameStore.set(updated.name, updated);
                setRequestStatus(REQUEST_STATUS.COMPLETED);
                onSave("success");
            }).catch(error => {
                setRequestStatus(REQUEST_STATUS.COMPLETED);
                onSave("error: " + error)
            });
        }
    }
}