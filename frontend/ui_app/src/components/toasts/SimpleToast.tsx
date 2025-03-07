import React, {useEffect, useState} from "react";
import {Toast, ToastContainer} from "react-bootstrap";
import styles from "./toast.module.scss";
import "./toast.module.scss";

export enum ToastType {
    Primary = 'Primary',
    Secondary = 'Secondary',
    Success = 'Success',
    Danger = 'Danger',
    Warning = 'Warning',
    Info = 'Info',
    Light = 'Light',
    Dark = 'Dark'
}

interface ToastProps {
    type?: ToastType;
    title?: string;
    message: string;
    onClose?: Function;
    show: boolean;
    autoHide?: boolean;
    position?: any;
}

/**
 * Bootstrap toast
 * documentation: https://react-bootstrap.netlify.app/components/toasts/#toasts
 * @constructor
 */
export default function SimpleToast(props: ToastProps) {
    const toastType = props && props.type ? props.type : ToastType.Light;
    const [show, setShow] = useState(true);

    const onClose = () => {
        setShow(false);
        props.onClose && props.onClose()
    }

    useEffect(() => {
        if (props.show !== show) {
            setShow(props.show);
        }
    }, [props.show])

    return (
        <ToastContainer className="p-3" position={props.position ?? "top-center"}>
            <Toast className="d-inline-block m-1"
                   bg={toastType.toLowerCase()}
                   onClose={onClose}
                   show={show}
                   delay={2000}
                   autohide={Boolean(props.autoHide)}>
                <Toast.Header className={styles.toastHeader}>
                    <strong className="me-auto">{props.title || "alert"}</strong>
                </Toast.Header>
                <Toast.Body className={`${styles.toastBody} ${className(toastType)}`}>
                    {props.message || "Hello, world! This is a toast message."}
                </Toast.Body>
            </Toast>
        </ToastContainer>
    )

    function className(toastType: ToastType) {
        switch (toastType) {
            case ToastType.Danger: return styles.danger;
            case ToastType.Success: return styles.success;
            case ToastType.Primary: return styles.primary;
            case ToastType.Info: return styles.info;
            default: return styles.info;
        }
    }
}