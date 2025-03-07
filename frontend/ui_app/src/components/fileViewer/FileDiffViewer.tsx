import React from "react";
import { FileType } from "../../servers/asset_server";
import { GlobalStore, StoreNames } from "../../stores";
import styles from "./file_diff_viewer.module.scss";
import { DownloadWithProgress } from "../progressBars";
import { CodeDiffEditor } from "../codeEditor";
import { jsonPretty } from "../../utils/utils";
import { AlertDismissible } from "../alerts";
import Button from "react-bootstrap/Button";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import {convertToCurrentTimeZone} from "../../utils";
import Content from "../../servers/asset_server/content";
import { downLoadBlobToDisk } from "./FileViewer"
import {Alert} from "../errorBoundary";

interface FileDiffViewerProps {
    url?: string;
    contentType?: string,
    fileName?: string;
    objectData?: any;
    prevURL?: string;
    prevObjectData?: any;
    styles?: any;
    base?: string;
    compare?: string;
    error?: any;
}

interface FileDiffViewerState {
    url?: string | null;
    fileName?: string;
    content?: any;
    format?: string;
    showProgress: boolean;
    showDiffProgress: boolean;
    showObjectData: boolean;
    error?: string | null;
    prevURL?: any | null;
    prevContent?: any;
    downloaded: boolean;
    prevDownloaded: boolean;
}

const SIZE_LIMIT: number = Content.DOWNLOAD_SIZE_LIMIT;

class FileDiffViewer extends React.Component<FileDiffViewerProps, FileDiffViewerState> {

    store?: GlobalStore;
    props: FileDiffViewerProps;

    constructor(props: FileDiffViewerProps) {
        super(props);
        this.props = props;
        this.state = {
            url: props.url,
            fileName: props.fileName,
            content: undefined,
            format: props.contentType,
            showProgress: false,
            showDiffProgress: false,
            showObjectData: false,
            error: props.error,
            prevURL: props.prevURL,
            prevContent: undefined,
            downloaded: false,
            prevDownloaded: false
        }
        this.store = GlobalStore.shared(StoreNames.fileContentStore, true);
    }

    componentDidUpdate(prevProps: Readonly<FileDiffViewerProps>, prevState: Readonly<any>, snapshot?: any) {
        // console.log("componentDidUpdate", prevProps, this.props);
        if (prevProps.url !== this.props.url) {
            if (this.props.url) {
                const contentId: string = this.props.objectData?.content?.id;
                this.store?.db.getItem(StoreNames.fileContentStore, contentId)
                    .then((existing: any) => {
                        if (existing) {
                            // let content: any = this.props.contentType === FileType.IMAGE?
                            //     window.URL.createObjectURL(existing.content) : existing.content;
                            this.setState(
                                {
                                    // showObjectData: false,
                                    ...this.state,
                                    url: this.props.url,
                                    content: existing.content,
                                    format: this.props.contentType,
                                    fileName: this.props.fileName,
                                    showProgress: false
                                });
                        } else {
                            this.setState({
                                ...this.state,
                                showProgress: true,
                                url: this.props.url,
                                format: this.props.contentType,
                                fileName: this.props.fileName
                            });
                        }
                    })
            } else {
                this.setState({
                    ...this.state,
                    showProgress: false,
                    content: undefined,
                    url: this.props.url,
                    format: this.props.contentType,
                    fileName: this.props.fileName
                });
            }
        }
        // if prev content exists
        if (prevProps.prevURL !== this.props.prevURL) {
            if (this.props.prevURL) {
                const prevContentId: string = this.props.prevObjectData?.content?.id;
                if (prevContentId) {
                    this.store?.db.getItem(StoreNames.fileContentStore, prevContentId)
                        .then((existing: any) => {
                            if (existing) {
                                this.setState(
                                    {
                                        ...this.state,
                                        prevURL: this.props.prevURL,
                                        prevContent: existing.content,
                                        showDiffProgress: false
                                    });
                            } else {
                                this.setState({
                                    ...this.state,
                                    prevURL: this.props.prevURL,
                                    showDiffProgress: true,
                                });
                            }
                        })
                } else {
                    this.setState({
                        ...this.state,
                        prevURL: this.props.prevURL,
                        showDiffProgress: true,
                    });
                }
            } else { //TODO: object data
                this.setState({
                    ...this.state,
                    prevContent: undefined,
                    prevURL: this.props.prevURL,
                    showDiffProgress: false,
                });
            }
        }
    }

    onDownloadComplete = (data: any) => {
        if (this.props.objectData?.content?.size > SIZE_LIMIT) {
            this.setState({...this.state, downloaded: false, showProgress: false})
            downLoadBlobToDisk(data, `${this.props.fileName}_${this.props.objectData?.created_at}`)
            return
        }
        this.setState({ content: data, showProgress: false })
        const contentId: string = this.props.objectData?.content?.id;
        if (contentId && this.state.format !== FileType.IMAGE) {
            this.store?.set(contentId, { content: data, timestamp: new Date().getTime() })
        }
    }

    onPrevDownloadComplete = (data: any) => {
        if (this.props.prevObjectData?.content?.size > SIZE_LIMIT) {
            this.setState({...this.state, prevDownloaded: false, showProgress: false})
            downLoadBlobToDisk(data, `${this.props.fileName}_${this.props.prevObjectData?.created_at}`)
            return
        }
        this.setState({ prevContent: data, showDiffProgress: false })
        const prevContentId: string = this.props.prevObjectData?.content?.id;
        if (prevContentId && this.state.format !== FileType.IMAGE) {
            this.store?.set(prevContentId, { content: data, timestamp: new Date().getTime() })
        }
    }

    render() {
        const content: any = this.state.content;
        const prevContent: any = this.state.prevContent;
        return (
            <div className={styles.container}>
                <div className={styles.header}>
                    <div className={styles.headerItem}>
                        <span>{`version: ${this.props.base}`}</span>
                        <div>
                            {this.props.prevObjectData && <AccessTimeIcon/>}
                            {this.props.prevObjectData &&
                            <span>{convertToCurrentTimeZone(this.props.prevObjectData?.created_at, "date")}</span>}
                        </div>
                    </div>
                    <div className={styles.headerItem}>
                        <span>{`version: ${this.props.compare}`}</span>
                        <div>
                            {this.props.objectData && <AccessTimeIcon/>}
                            {this.props.objectData &&
                            <span>{convertToCurrentTimeZone(this.props.objectData.created_at, "date")}</span>}
                        </div>
                    </div>
                </div>
                <div>
                    {this.viewDiff(prevContent, content)}
                </div>
                {this.renderError(this.state.error || this.props.error)}
            </div>
        )
    }

    viewDiff(prevContent: any, content: any) {
        if ((this.state.url || this.state.prevURL) &&
            (this.props.objectData?.content?.size > SIZE_LIMIT ||
                this.props.prevObjectData?.content?.size > SIZE_LIMIT)) {
                return (
                    <div>
                        {this.downloadButton()}
                    </div>
                )
            }
        return (
            <div>
                {
                    (this.state.url || this.state.prevURL) ?
                        <div>
                            {
                                (this.state.showProgress || this.state.showDiffProgress) ?
                                    <div className={styles.diffProgressContainer}>
                                        {
                                            this.state.showProgress && this.state.url &&
                                            <div className={styles.progressContainer}>
                                                <DownloadWithProgress url={this.state.url}
                                                    contentType={this.state.format || ''}
                                                    onComplete={this.onDownloadComplete} />
                                            </div>
                                        }
                                        {
                                            this.state.showDiffProgress && this.props.prevURL &&
                                            <div className={styles.progressContainer}>
                                                <DownloadWithProgress url={this.state.prevURL}
                                                    contentType={this.state.format || ''}
                                                    onComplete={this.onPrevDownloadComplete} />
                                            </div>
                                        }
                                    </div>
                                    :
                                    <div>
                                        {this.renderDiff(prevContent, content, this.state.format)}
                                    </div>
                            }
                        </div>
                        :
                        <div>
                            {this.renderDiff(this.props.prevObjectData, this.props.objectData, FileType.JSON)}
                        </div>
                }
            </div>
        )
    }

    renderDiff(prevContent: any, content: any, format: any) {
        switch (format) {
            case FileType.IMAGE: {
                return (
                    <div className={styles.imageDiffViewer}>
                        <div className={styles.imageDiffLeft}><img src={prevContent} alt={'None'} /></div>
                        <div className={styles.imageDiffRight}><img src={content} alt={'None'} /></div>
                    </div>
                )
            }
            default: {
                return (
                    <div className={styles.diffViewer}>
                        <CodeDiffEditor language={this.state.format}
                            original={this.formatContent(prevContent, format)}
                            modified={this.formatContent(content, format)}
                            readonly={true}
                            className={styles.diffViewer} />
                    </div>
                )
            }
        }
    }

    formatContent(data: any, contentType?: string) {
        switch (contentType) {
            case FileType.JSON:
                return jsonPretty(data);
            default:
                return data;
        }
    }

    renderError(error: any) {
        if (!error) return null;
        return (
            <Alert variant={"error"} title={"Oh snap! You got an error!"} description={[error]}/>
            // <AlertDismissible className={styles.alert}
            //     variant={"danger"}>
            //     <p>{error.toString()}</p>
            // </AlertDismissible>
        )
    }

    downloadButton() {
        return (
            <div className={styles.imageDiffViewer}>
                <div className={styles.imageDiffLeft}>
                    {
                        this.state.prevURL ?
                        <div className={styles.downloadButton}>
                        <Button variant="primary"
                            onClick={() => this.setState(
                            {...this.state, prevDownloaded: true, showProgress: true})}>
                            Download</Button>
                        <p>Large file is not renderer by default.</p>
                        </div>
                        :
                        <div className={styles.downloadButton}>Content Not Found</div>
                    }
                </div>
                {
                    this.state.prevDownloaded && this.state.showProgress && this.state.prevURL &&
                    <div className={styles.progressContainer}>
                        <DownloadWithProgress url={this.state.prevURL}
                                              contentType={this.state.format || "json"}
                                              saveAsUrl={true}
                                              onComplete={this.onPrevDownloadComplete}/>
                    </div>
                }
                <div className={styles.imageDiffRight}>
                    {
                        this.state.url ?
                        <div className={styles.downloadButton}>
                        <Button variant="primary"
                            onClick={() => this.setState(
                            {...this.state, downloaded: true, showProgress: true})}>
                            Download</Button>
                        <p>Large file is not renderer by default.</p>
                        </div>
                        :
                        <div className={styles.downloadButton}>Content Not Found</div>
                    }
                {
                    this.state.downloaded && this.state.showProgress && this.state.url &&
                    <div className={styles.progressContainer}>
                        <DownloadWithProgress url={this.state.url}
                                              contentType={this.state.format || "json"}
                                              saveAsUrl={true}
                                              onComplete={this.onDownloadComplete}/>
                    </div>
                }
                </div>
            </div>
        )
    }

}

export default FileDiffViewer;
