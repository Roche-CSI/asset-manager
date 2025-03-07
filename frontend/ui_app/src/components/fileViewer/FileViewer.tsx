import React from "react";
import {FileType, Asset} from "../../servers/asset_server";
import {GlobalStore, StoreNames} from "../../stores";
import styles from "./file_viewer.module.scss";
import {DownloadWithProgress} from "../progressBars";
import ObjectDataRenderer from "./ObjectDataRenderer";
import { CodeEditor } from "../codeEditor";
import { jsonPretty } from "../../utils/utils";
import { yamlError, jsonError, convertToCurrentTimeZone} from "../../utils";
import {formatBytes} from "../../utils/fileUtils";
import {Alert} from "../errorBoundary";
import { YamlRenderer } from './YamlRenderer';
import { CopyButton } from "../copyButton";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import Content, {ContentInterface} from "../../servers/asset_server/content";
import Button from "react-bootstrap/Button";
import { CsvRenderer, HtmlRenderer } from "../fileRenderers";
import { MarkdownEditor } from "../markDownEditor";
import {Calendar, CircleUser, SquareMenu} from "lucide-react";
import FileBreadCrumb from "./FileBreadCrumb";

export function downLoadBlobToDisk(blobUrl: any, fileName?: string) {
    let link = document.createElement("a");
    link.setAttribute("id", "tempDownloadLink");
    link.href = blobUrl;
    link.download = fileName || "";
    document.body.appendChild(link);
    let downloadLink: any = document.getElementById("tempDownloadLink")
    downloadLink && downloadLink.click()
    downloadLink.remove()
}


interface FileViewerProps {
    url: string;
    contentType: string,
    fileName: string;
    objectData: any;
    error?: any;
    header?: boolean;
    asset?: Asset;
}

interface FileViewerState {
    url: string | null;
    fileName: string;
    content?: any;
    format: string;
    showProgress: boolean;
    isProxy: boolean;
    error: string | null;
    line: number | null;
    downloaded: boolean;
}

const SIZE_LIMIT: number = Content.DOWNLOAD_SIZE_LIMIT;

class FileViewer extends React.Component<FileViewerProps, FileViewerState> {

    store?: GlobalStore;
    props: FileViewerProps;

    constructor(props: FileViewerProps) {
        super(props);
        this.props = props;
        this.state = {
            url: this.props.url,
            fileName: props.fileName,
            content: undefined,
            format: props.contentType || "json",
            showProgress: false,
            isProxy: this.props.objectData?.content?.meta?.proxy,
            error: props.error,
            line: null,
            downloaded: false,
        }
        this.store = GlobalStore.shared(StoreNames.fileContentStore, true);
        this.setLineNumber = this.setLineNumber.bind(this);
    }

    componentDidUpdate(prevProps: Readonly<FileViewerProps>, prevState: Readonly<any>, snapshot?: any) {
        // console.log("componentDidUpdate", prevProps, this.props);
        if (this.props.url) {
            if (prevProps.url !== this.props.url) {
                const contentId: string = this.props.objectData?.content?.id;
                this.store?.db.getItem(StoreNames.fileContentStore, contentId)
                    .then((existing: any) => {
                        let isProxy: boolean = this.props.objectData?.content?.meta?.proxy;
                        if (existing) {
                            // let content: any = this.props.contentType === FileType.IMAGE?
                            //     window.URL.createObjectURL(existing.content) : existing.content;
                            this.setState(
                                {
                                    ...this.state,
                                    url: isProxy? null: this.props.url,
                                    content: existing.content,
                                    format: this.props.contentType,
                                    fileName: this.props.fileName,
                                    showProgress: false,
                                    error: this.props.error || (isProxy && "Proxy file is not supported.")
                                });
                            // this.validateContent(existing.content, this.state.format)
                        } else {
                            this.setState({
                                ...this.state,
                                showProgress: true,
                                url: isProxy? null: this.props.url,
                                format: this.props.contentType,
                                fileName: this.props.fileName,
                                error: this.props.error || (isProxy && "Proxy file is not supported.")
                            });
                        }
                    })
            }
        }
    }

    onDownloadComplete = (data: any) => {
        if (this.props.objectData?.content?.size > SIZE_LIMIT) {
            this.setState({...this.state, downloaded: false, showProgress: false})
            downLoadBlobToDisk(data, this.props.fileName)
            return
        }
        this.setState({ content: data.toString(), showProgress: false }, () => {
            this.validateContent(data, this.state.format);
            
            const contentId: string = this.props.objectData?.content?.id;
            if (contentId && this.state.format !== FileType.IMAGE) {
                this.store?.set(contentId, { content: data, timestamp: new Date().getTime() });
            }
        });
    }

    render() {
        const content = this.state.content;
        return (
            <div className="">
                {this.props.header && this.header(this.props.objectData?.content)}
                <div>
                    {this.renderError(this.props.error || this.state.error)}
                    {this.viewFile(content)}
                </div>
            </div>
        )
    }

    header(contentObject: ContentInterface) {
        if(!contentObject) {
            return <div className={styles.cardHeader}></div>
        }
        return (
            <div className="px-4 py-4 border-x border-t border-base-300 rounded-t-md bg-base-200">
                {/* <div className={styles.headerItem}>
                        <span>{this.state.fileName || this.props.fileName}</span>
                </div> */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center text-sm space-x-8">
                    <span className="flex items-center space-x-2">
                        <CircleUser className="h-4 w-4"/>
                        <span>{contentObject.created_by}</span>
                    </span>
                        <span className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4"/>
                        <span>{convertToCurrentTimeZone(contentObject.created_at, "date")}</span>
                    </span>
                        <span className="flex items-center space-x-2">
                        <SquareMenu className="w-4 h-4"/>
                        <span>{formatBytes(contentObject.size)}</span>
                    </span>
                        {/*<div className={styles.fileInfoDivider}></div>*/}
                        {/*    {this.state.line && <span>{`${this.state.line} lines`}</span>}*/}
                    </div>
                    <div className={styles.headerItem}>
                        <CopyButton textToCopy={this.state.content || this.props.objectData}
                                    styles={styles}/>
                    </div>
                </div>
            </div>
        )
    }
    
    viewFile(content: any) {
        if ((this.props.objectData?.content?.size > SIZE_LIMIT) && this.state.url) {
            return (
                <div>
                    {this.downloadButton()}
                </div>
            )
        }
        return (
            <div>
                {
                    this.state.url ?
                        <div>
                            {
                                this.state.showProgress &&
                                <div className={styles.progressContainer}>
                                    <DownloadWithProgress url={this.state.url}
                                                          contentType={this.state.format}
                                                          onComplete={this.onDownloadComplete}/>
                                </div>
                            }
                            {this.renderContent(content, this.state.format)}
                        </div>
                        :
                        <ObjectDataRenderer objectData={this.props.objectData}/>
                }
            </div>
        )
    }
    
    renderContent(content: any, format: string) {
        switch (format) {
            case FileType.IMAGE: {
                return <div className={styles.imageViewer}><img src={content} alt={''}/></div>
            }
            case FileType.YAML: {
                const fileName: string = this.state.fileName || this.props.fileName;
                const isPackageYaml = fileName.includes("package.yaml") || fileName.includes("pkg.yaml");
                return (
                    <div className={`${styles.fileViewer} ${styles.yaml}`}>
                        <YamlRenderer isPackageYaml={isPackageYaml}
                                      content={content}
                                      readonly={true}
                                      setLineNumber={this.setLineNumber} />
                    </div>
                )
            }
            case FileType.CSV: {
                return (
                    <div className={`${styles.fileViewer} ${styles.csv}`}>
                        <CsvRenderer content={content} />
                    </div>
                )
            }
            case FileType.MD: {
                return (
                    <div className={`${styles.fileViewer}`}>
                        <MarkdownEditor mdContent={content} mode={"preview"}/>
                    </div>
                )
            }
            case FileType.HTML: {
                return (
                    <div className={`${styles.fileViewer}`}>
                        <HtmlRenderer content={content} asset={this.props.asset}/>
                    </div>
                )
            }
            default: {
                return (
                    <div className={styles.fileViewer}>
                        <CodeEditor language={this.state.format}
                                    value={this.formatContent(content, this.state.format)}
                                    readonly={true}
                                    setLineNumber={this.setLineNumber} />
                    </div>

                )
            }
        }
    }

    formatContent(data: any, contentType: string) {
        switch (contentType) {
            case FileType.JSON:
                return jsonPretty(data);
            default:
                return data;
        }
    }

    validateContent(data: any, contentType:string) {
        switch (contentType) {
            case FileType.YAML:
                if (this.props.fileName === "Dockerfile") {
                    return
                }
                const errorYaml = yamlError(data);
                if (errorYaml) {
                    this.setState({...this.state, error: errorYaml})
                }
                return;
            case FileType.JSON:
                const errorJson = jsonError(data);
                if (errorJson) {
                    this.setState({...this.state, error: errorJson})
                }
                return;
            default:
                return;
        }
    }

    renderError(error: any) {
        if (!error) return null;
        return (
            <Alert variant={"error"} title={"This file has the following error:"} description={[error.toString()]}/>
        )
    }

    setLineNumber(lineNum: number) {
        this.setState({...this.state, line: lineNum})
    }

    downloadButton() {
        return (
            <div>
                <div className={styles.downloadButton}>
                    <button className="btn btn-sm btn-secondary rounded-md"
                        onClick={() => this.setState(
                        {...this.state, downloaded: true, showProgress: true})}>
                        Download</button>
                    <p>File is too large to display here</p>
                </div>
                {
                    this.state.downloaded && this.state.showProgress && this.state.url &&
                    <div className={styles.progressContainer}>
                        <DownloadWithProgress url={this.state.url}
                                              contentType={this.state.format}
                                              saveAsUrl={true}
                                              onComplete={this.onDownloadComplete}/>
                    </div>
                }
            </div>
        )
    }
}

export default FileViewer;
