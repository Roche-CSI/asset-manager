import React, { useCallback, useEffect, useState } from "react";
import HorizontalFlow from "./HorizontalFlow";
import { Asset, AssetRef } from "../../servers/asset_server";
import { AssetVersion } from "../../servers/asset_server/assetVersion";
import { StoreNames, useStore } from "../../stores";
import { useQuery } from "../../utils/utils";
import { useParams } from "react-router-dom";
import { GraphFlow } from "./flowGraph";
import { SpinIndicator } from '../spinIndicator';
import { ToggleButtons } from "../toggleButtons";
import { AssetRefTable } from "../tables/assetRefTable";
import { AlertDismissible } from "../alerts";
import { Button } from "react-bootstrap";
import { isEmptyObject } from "../../utils/utils";
import VersionSelector from "../assetBrowser/VersionSelector";
import styles from "./graph_view.module.scss";
import 'reactflow/dist/style.css';

interface GrapherProps {
    asset: Asset;
    className: string
}

export default function AssetGraphView(props: GrapherProps) {
    // version
    const { class_name, seq_id } = useParams();
    const version = useQuery().get('version');
    const assetVersionName: string = props.asset.versionName(class_name as string, version as string);
    const assetName: string = `${class_name}/${seq_id}`;
    const versionName: string = `${class_name}/${seq_id}/${version}`
    console.log(class_name, seq_id, version, versionName);
    const options: string[] = ['graph', "table"];
    // store
    const refStore = useStore(StoreNames.assetRefStore)
    const outboundStore = useStore(StoreNames.assetOutboundStore)
    const userStore = useStore(StoreNames.userStore);
    // state
    const [inboundRefs, setInboundRefs] = useState<AssetRef[] | undefined>(refStore.get(versionName))
    const [outboundRefs, setOutboundRefs] = useState<AssetRef[] | undefined>(outboundStore.get(versionName))
    const [view, setView] = useState<string>(options[0]);
    const [loading, setLoading] = useState<boolean>(false);
    const [activeVersion, setActiveVersion] = useState<any>(null);
    const [nodes, setNodes] = useState<any[]>([]);
    const [edges, setEdges] = useState<any[]>([]);
    const [error, setError] = useState<string>("")
    const [showAll, setShowAll] = useState<boolean>(false)

    const getVersion = useCallback((ver: any, callback: Function) => {
        if (!ver || ver.number !== version || ver.asset.id !== props.asset.id) {
            setLoading(true)
            AssetVersion.get(AssetVersion.URL(),
                {
                    asset_id: props.asset.id,
                    user: userStore.get("user").username,
                }).then((data: any) => {
                    props.asset.versions = data.map((o: any) => new AssetVersion(o, props.asset))
                    setActiveVersion((activeVersion: any) => {
                        return props.asset.getVersion(version)
                    });
                    callback && callback();
                }).catch((error: any) => {
                    setError(error.message)
                    setLoading(false)
                })
        } else {
            setActiveVersion((activeVersion: any) => {
                return ver
            });
            callback && callback();
        }
    }, [props.asset, userStore, version])

    const updateFlow = (inboundRefs: AssetRef[], outboundRefs: AssetRef[]) => {
        let graph = new GraphFlow(inboundRefs, outboundRefs)
        let [nodes, edges] = graph.createGraph()
        setNodes(nodes)
        setEdges(edges)
    }

    function fetchRefs() {
        AssetRef.getRefs(userStore.get("user").username, userStore.get("active_project"),
            [assetName], [version])
            .then((data) => {
                const refs: any = data?.[assetName]?.[version]
                let inboundRefs = refs?.["depends_on"].map((o: any, index: number) => new AssetRef(o))
                let outboundRefs = refs?.["dependents"].map((o: any, index: number) => new AssetRef(o))
                // set in store
                refStore.set(versionName, inboundRefs)
                outboundStore.set(versionName, outboundRefs)
                // update state
                setInboundRefs(inboundRefs)
                setOutboundRefs(outboundRefs)
                updateFlow(inboundRefs, outboundRefs)
                setLoading(false)
            }).catch((error: any) => {
                setError(`Failed finding asset refs: ${error.message}`)
                setLoading(false)
            })
    }

    const updateRefs = () => {
        let newInboundRefs: any = refStore.get(versionName)
        let newOutboundRefs: any = outboundStore.get(versionName)
        if (!newInboundRefs || !newOutboundRefs) {
            fetchRefs();
        } else {
            setInboundRefs(newInboundRefs)
            setOutboundRefs(newOutboundRefs)
            updateFlow(newInboundRefs, newOutboundRefs)
            setLoading(false)
        }
    }

    useEffect(() => {
        if (assetVersionName !== versionName) {
            return;
        }
        let ver = props.asset.getVersion(version);
        getVersion(ver, updateRefs);
    }, [props.asset, class_name, seq_id, version])

    const GraphView = () => (
        <div>
            {nodes.length > 0 && edges.length > 0 ?
                <HorizontalFlow nodes={nodes} edges={edges} /> :
                <h5>No inbound and outbound assets found</h5>}
        </div>
    )

    const TableView = () => {
        return (
            <div className={styles.tableContainer}>
                <div className={styles.inboundTable}>
                    <div className={styles.title}>
                        Inbound Assets:
                    </div>
                    <div className={styles.table}>
                        <AssetRefTable refs={inboundRefs || []} inbound={true} />
                    </div>
                </div>
                <div className={styles.outboundTable}>
                    <div className={styles.title}>
                        Outbound Assets:
                    </div>
                    <div className={styles.table}>
                        <AssetRefTable refs={outboundRefs || []} inbound={false} />
                    </div>
                </div>
            </div>
        )
    }

    const allRefsTable = () => {
        if (isEmptyObject(props.asset.refs)) {
            return null
        }
        let version_numbers: string[] = Object.keys(props.asset.refs).sort()
        return (
            <div>
                {version_numbers.map((version_number: string) => {
                    let versionRef: any = props.asset.refs[version_number]
                    let inboundRefs = versionRef?.["depends_on"].map((o: any, index: number) => new AssetRef(o))
                    let outboundRefs = versionRef?.["dependents"].map((o: any, index: number) => new AssetRef(o))
                    return (
                        <div key={version_number} className={styles.refTable}>
                            <span className={styles.title}>{version_number}</span>
                            <div>
                                <AssetRefTable refs={inboundRefs || []} inbound={true} />
                                <AssetRefTable refs={outboundRefs || []} inbound={false} />
                            </div>
                        </div>
                    )
                })}
            </div>
        )
    }

    function refView() {
        return (
            <div className={styles.card}>
                <div className={styles.toggleContainer}>
                    <div className={styles.toggleButton}>
                        <ToggleButtons value={view}
                            options={options}
                            setValue={setView} />
                    </div>
                </div>
                <div>
                    {view === "graph" ?
                        <GraphView />
                        :
                        <div className={styles.tableView}>
                            <div className={styles.showAllButton}>
                                <Button onClick={() => fetchAllRefs()}
                                    size={"sm"}
                                    variant="outline-primary">
                                    {showAll ? "Back" : "View All"}
                                </Button>
                            </div>
                            <div>
                                {showAll ? allRefsTable() : <TableView />}
                            </div>
                        </div>
                    }
                </div>
            </div>
        )
    }

    return (
        <div className={styles.page}>
            {error && <AlertDismissible>{error}</AlertDismissible>}
            {loading ?
                <SpinIndicator message={"Loading..."} />
                :
                <div>
                    {/* <div className={styles.versionSelector}>
                        <VersionSelector versions={props.asset.versions} activeVersion={activeVersion}
                            asset={props.asset} />
                    </div> */}
                    <div>
                        {refView()}
                    </div>
                </div>
            }
        </div>
    )

    function fetchAllRefs() {
        if (!isEmptyObject(props.asset.refs)) {
            setShowAll(!showAll)
            return
        }
        setLoading(true)
        AssetRef.getRefs(userStore.get("user").username, userStore.get("active_project"), [assetName])
            .then((data) => {
                // console.log(data[assetName])
                props.asset.updateRefs(data[assetName])
                setShowAll(!showAll)
                setLoading(false)
            }).catch((error: any) => {
                setError(`Failed finding asset refs: ${error.message}`)
                setLoading(false)
            })
    }
}

