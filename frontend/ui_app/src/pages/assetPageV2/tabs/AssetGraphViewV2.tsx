import React, {useCallback, useEffect, useState} from "react";
import HorizontalFlow from "../../../components/assetGrapher/HorizontalFlow";
import {Asset, AssetClass, AssetRef} from "../../../servers/asset_server";
import {AssetVersion} from "../../../servers/asset_server/assetVersion";
import {StoreNames, useStore} from "../../../stores";
import {useQuery} from "../../../utils/utils.ts";
import {useParams} from "react-router-dom";
import {GraphFlow} from "../../../components/assetGrapher/flowGraph";
import Spinner from "../../../components/spinner/Spinner";
import {ToggleButtons} from "../../../components/toggleButtons";
import {AssetRefTable} from "../../../components/tables/assetRefTable";
import {Alert} from "../../../components/errorBoundary";
import {Button} from "react-bootstrap";
import {isEmptyObject} from "../../../utils/utils.ts";
import VersionSelector from "../../../components/assetBrowser/VersionSelector";
import styles from "../../../components/assetGrapher/graph_view.module.scss";
import 'reactflow/dist/style.css';
import Switcher from "../../../components/assetHistory/Switcher";
import HorizontalFlowV2 from "../../../components/assetGrapher/HorizontalFlowV2";
import GraphGenerator from "../../../components/assetGrapher/GraphGenerator";
import RefsTable from "../RefTable.tsx";

interface GrapherProps {
	asset: Asset;
	className: string
}

export default function AssetGraphViewV2(props: GrapherProps) {
	// version
	const {project_id, class_name, seq_id} = useParams();
	const version = useQuery().get('version');
	const assetVersionName: string = props.asset.versionName(class_name as string, version as string);
	const assetName: string = `${class_name}/${seq_id}`;
	const versionName: string = `${class_name}/${seq_id}/${version}`
	// console.log(class_name, seq_id, version, versionName);
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
	const [error, setError] = useState<string>("");
	const [showAll, setShowAll] = useState<boolean>(false);
	const classIdStore = useStore(StoreNames.classIdStore);
	const [assetClasses, setAssetClasses] = useState<any>(classIdStore.data);
	
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
    
    const addClassDataToRefs = (refs: AssetRef[]) => {
        // cast to map
        refs.forEach((ref: AssetRef) => {
            const srcClass: AssetClass = classIdStore.data?.[ref.src_version.asset_class];
            ref.src_version.class_type = srcClass?.class_type;
            ref.src_version.class_title = srcClass?.title;
            
            const dstClass = classIdStore.data?.[ref.dst_version.asset_class];
            ref.dst_version.class_type = dstClass?.class_type;
            ref.dst_version.class_title = dstClass?.title;
        })
    }
	
	const updateFlow = (inboundRefs: AssetRef[], outboundRefs: AssetRef[]) => {
		// add class-data to nodes
		if (Object.values(classIdStore.data).length === 0) {
			return;
		}
        addClassDataToRefs(inboundRefs);
        addClassDataToRefs(outboundRefs);
		
		console.log("inboundRefs:", inboundRefs);
		console.log("outboundRefs:", outboundRefs);
		
		let graph = new GraphGenerator(inboundRefs, outboundRefs)
		let [nodes, edges] = graph.createGraph()
		setNodes(nodes)
		setEdges(edges)
	}
	
	function fetchRefs() {
		AssetRef.getRefs(userStore.get("user").username, userStore.get("active_project"),
				[assetName], [version])
			.then((data) => {
				const refs: any = data?.[assetName]?.[version]
				const inboundRefs: AssetRef[] = refs?.["depends_on"].map((o: any, index: number) => new AssetRef(o))
				const outboundRefs: AssetRef = refs?.["dependents"].map((o: any, index: number) => new AssetRef(o))
				// set in store
				refStore.set(versionName, inboundRefs)
				outboundStore.set(versionName, outboundRefs)
				// update state
				setInboundRefs(inboundRefs)
				setOutboundRefs(outboundRefs)
				// add class-data to nodes
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

	const fetchVersion = (version: string) => {
		if (assetVersionName === versionName) {
			let ver = props.asset.getVersion(version);
			getVersion(ver, updateRefs);
		}
	}
	
	const fetchClassListFromServer = () => {
		setLoading(true)
		let id_map: any = {};
		let name_map: any = {};
		AssetClass.getFromServer(null, null, project_id).then((data: any[]) => {
			data.forEach((o: any, index: number) => {
				let asset_class = new AssetClass(o);
				id_map[o.id] = asset_class;
				name_map[o.name] = asset_class;
			})
			classIdStore.set(null, id_map);
			classIdStore.didFullUpdate = true;
            setAssetClasses(classIdStore.data)
			fetchVersion(version)
		}).catch((error: any) => {
			console.log("error:", error)
		})
	}
	
	// get classList if its missing
	useEffect(() => {
		if (!assetClasses || Object.values(assetClasses).length === 0) {
			fetchClassListFromServer();
		} else {
			fetchVersion(version)
		}
	}, [props.asset, class_name, seq_id, version])
	
	const GraphView = () => (
		<div>
			{nodes.length > 0 && edges.length > 0 ?
				<HorizontalFlowV2 nodes={nodes} edges={edges}/> :
				<h5>No inbound and outbound assets found</h5>}
		</div>
	)
	
	const TableView = () => {
		// console.log("table view inbound refs", JSON.stringify(inboundRefs))
		// console.log("table view outbound refs", JSON.stringify(outboundRefs))
		return (
			<div className={styles.tableContainer}>
				<div>
					<div className={styles.title}>
						Inbound Assets:
					</div>
					<div>
						<RefsTable refs={inboundRefs || []}/>
					</div>
				</div>
				<div className={styles.outboundTable}>
					<div className={styles.title}>
						Outbound Assets:
					</div>
					<div className={styles.table}>
						<AssetRefTable refs={outboundRefs || []} inbound={false}/>
					</div>
				</div>
			</div>
		)
	}
	
	const allRefsTable = () => {
		if (isEmptyObject(props.asset.refs)) {
			return null
		}
		console.log("refs: ", props.asset.refs);
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
								<AssetRefTable refs={inboundRefs || []} inbound={true}/>
								<AssetRefTable refs={outboundRefs || []} inbound={false}/>
							</div>
						</div>
					)
				})}
			</div>
		)
	}
	
	function refView() {
		return (
			<div className="mt-6">
				<div className="mb-6 flex justify-between w-full">
					<div className="text-lg text-neutral font-semibold">Asset Lineage</div>
					<Switcher value={view} options={options} setValue={setView} size={"sm"}/>
				</div>
				<div>
					{view === "graph" ?
						<GraphView/>
						:
						<div className={styles.tableView}>
							{/*<div className={styles.showAllButton}>*/}
							{/*    <Button onClick={() => fetchAllRefs()}*/}
							{/*            size={"sm"}*/}
							{/*            variant="outline-primary">*/}
							{/*        {showAll ? "Back" : "View All"}*/}
							{/*    </Button>*/}
							{/*</div>*/}
							<div>
								{showAll ? allRefsTable() : <TableView/>}
							</div>
						</div>
					}
				</div>
			</div>
		)
	}
	
	return (
		<div className="">
			{error && <Alert variant={"error"} title={"Oh snap! You got an error!"} description={[error]}/>}
			{loading ?
				<div className='mt-32'>
					<Spinner message={"Loading..."}/>
				</div>
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

