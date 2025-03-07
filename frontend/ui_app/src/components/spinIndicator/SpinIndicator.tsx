import React from "react";
import styles from "./spinner.module.scss";
import {Button, Spinner as BootstrapSpinner} from "react-bootstrap";

interface Props {
    message?: string
    className?: string
}

export default function SpinIndicator(props: Props) {
    return (
        <div className={props.className || styles.spinnerContainer}>
            <Button variant="primary" disabled>
                <BootstrapSpinner
                    as="span"
                    animation="grow"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                />
                <span className={styles.spinnerLabel}>{props.message || "Loading..."}</span>
            </Button>
        </div>
    )
}