import React from "react";
import styles from "./alert.module.scss";
import {Alert, Button} from "react-bootstrap";

interface Props {
    className?: string;
    title?: string;
    onSuccess?: Function;
    onCancel?: Function;
    successLabel?: string;
    cancelLabel?: string;
    children?: any;
    variant?: string;
    showButton?: boolean;
}


/**
 * class component because of ease of HOC
 * @constructor
 */
export default class AlertDismissible extends React.Component<Props, any>{

    props: Props;
    constructor(props: Props) {
        super(props);
        this.props = props;
        this.state = {show: true};
    }

    onCancel = (e: any) => {
        this.setState({show: false}, () => {
            this.props.onCancel && this.props.onCancel();
        });
    }

    onSuccess = (e: any) => {
        console.log(this.props.onSuccess);
        this.setState({show: false}, () => {
            this.props.onSuccess && this.props.onSuccess();
        });
    }

    render() {
        return (
            <div className={`${this.props.className || ""} ${styles.defaultStyle}`}>
                <Alert show={this.state.show} variant={this.props.variant || "danger"}>
                    <Alert.Heading className={styles.header}>{this.props.title}</Alert.Heading>
                    {this.props.children || this.defaultContent()}
                    {(this.props.cancelLabel || this.props.cancelLabel) && <hr />}
                    <div className={`${styles.footer}`}>
                        {this.props.cancelLabel &&
                            <Button onClick={this.onCancel}
                                variant="outline-secondary"
                                className={styles.alertButton}>
                            {this.props.cancelLabel || 'Close me y\'all!'}
                        </Button>
                        }
                        {this.props.successLabel &&
                        <Button onClick={this.onSuccess}
                                variant="outline-primary"
                                className={styles.alertButton}>
                            {this.props.successLabel || 'Close me y\'all!'}
                        </Button>
                        }
                    </div>
                </Alert>
                {this.props.showButton &&
                    !this.state.show && 
                    <Button onClick={() => this.setState({show: true})}>Show Alert</Button>
                }
            </div>
        );
    }

    defaultContent() {
        return (
            <p>
                Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget
                lacinia odio sem nec elit. Cras mattis consectetur purus sit amet
                fermentum.
            </p>
        )
    }

}
