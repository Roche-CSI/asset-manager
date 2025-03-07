import React, {useEffect, useState} from "react";
import {ProgressBar} from "../progressBar";
import styles from "./poll.module.scss";
import {fetchGet} from "../../../servers/base/restUtils";
import {StoreNames, useStore} from "../../../stores";

interface Props {
    label?: string;
    progressInterval: number; // update progress bar every # seconds
    pollInterval: number; // poll every # seconds
    numPolls: number; // number of polls
    pollURL: string; // url to poll
    breakCondition?: Function;
    onClose: Function
}
const MAX_POLLS = 100;

export default function PollWithProgress(props: Props) {
    const [progress, setProgress] = useState(0);
    const maxDuration = props.pollInterval * Math.min(props.numPolls, MAX_POLLS);
    const userStore = useStore(StoreNames.userStore);

    useEffect(() => {
        let elapsed = 0;
        let breakCondition: Function | undefined = props.breakCondition;
        if (!breakCondition) {
            breakCondition = (data: any) => {
                return elapsed >= maxDuration;
            }
        }
        const interval = setInterval(() => {
            elapsed += props.progressInterval;
            if (elapsed > maxDuration) {
                props.onClose("timeout");
            }
            if (elapsed % props.pollInterval === 0) {
                console.log("make poll request: ", elapsed);
                fetchGet(props.pollURL, {user: userStore.get("user").username}).then((res: any) => {
                    console.log("response:", res);
                    if (breakCondition && breakCondition(res)) {
                        setProgress((progress: number) => 100);
                        // add a delay to show progress completion
                        setTimeout(() => {
                            props.onClose("success", res);
                        }, 500)

                    }
                }).catch(error => {
                    console.log("error:", error);
                    props.onClose("error", null);
                })
            }else {
                let progressIncrement = Math.min(100 - progress, (props.progressInterval / maxDuration) * 100);
                setProgress((progress: number) => progress + progressIncrement);
            }

        }, props.progressInterval * 1000);
        return () => clearInterval(interval);
    }, []);

    // console.log("progress:", progress);

    return (
        <div className={styles.container}>
            {props.label && <h5 className={styles.label}>{props.label}</h5>}
            <div className={styles.progress}>
                <ProgressBar value={progress}/>
            </div>
        </div>
    )
}