import React from "react";
import Box from "@mui/material/Box";
import {ProgressBar} from "../progressBar";
import {FileHandler} from "../../../servers/asset_server";
import styles from "./downlod.module.scss";
import {Alert} from "../../errorBoundary";


interface Props {
    url: string;
    contentType: string;
    saveAsUrl?: boolean;
    onComplete?: Function
}

export default function DownloadWithProgress(props: Props) {
    const [progress, setProgress] = React.useState(0);
    const [error, setError] = React.useState<any>(null);

    const updateProgress = (received: number, max: number) => {
        setProgress(Math.round((received / max) * 100));
    }

    React.useEffect(() => {
        // const timer = setInterval(() => {
        //     setProgress((prevProgress) => (prevProgress >= 100 ? 10 : prevProgress + 10));
        // }, 800);
        // return () => {
        //     clearInterval(timer);
        // };
        new FileHandler().downloadWithProgress(
            props.url,
            props.contentType,
            props.saveAsUrl,
            updateProgress
            )?.then((data: any) => {
            setProgress(100);
            props.onComplete && props.onComplete(data);
        }).catch((error) => {
            console.error(error)
            setError(error);
        })
    }, [props.url]);

    return (
        <div className="w-full px-2 py-1">
            {!error && <ProgressBar value={progress}/>}
            {error && renderError(error)}
        </div>
    );

    function renderError(error: any) {
        return (
            <Alert variant={"error"} title={"Oh snap! You got an error!"} description={[error.toString()]}/>
            // <Alert variant="danger" onClose={() => setError(null)} dismissible>
            //     <Alert.Heading>Oh snap! You got an error!</Alert.Heading>
            //     <p>
            //         {error.toString()}
            //     </p>
            // </Alert>
        )
    }
}
