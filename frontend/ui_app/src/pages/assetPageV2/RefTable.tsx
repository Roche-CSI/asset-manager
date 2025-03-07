import React, { useState } from 'react';
import { MoreVertical, Plus, Pencil, Trash2, AlertCircle } from 'lucide-react';

const RefsTable = ({refs}) => {
	const [data, setData] = useState(refs);
	const [editingId, setEditingId] = useState(null);
	const [openMenuId, setOpenMenuId] = useState(null);
	const [deleteConfirmId, setDeleteConfirmId] = useState(null);
	
	const addNewRow = () => {
		const newRow = {
			id: Math.max(...data.map(item => item.id)) + 1,
			dst_version: {
				asset: "",
				asset_class: "",
				id: 0,
				name: "new_model/1/0.0.0"
			},
			src_version: {
				asset: "",
				asset_class: "",
				id: 0,
				name: "new_source/1/0.0.0"
			},
			created_at: new Date().toLocaleString(),
			created_by: "user",
			label: "new_asset",
			properties: [],
			tags: []
		};
		setData([...data, newRow]);
		setEditingId(newRow.id);
	};
	
	const deleteRow = (id) => {
		setData(data.filter(row => row.id !== id));
		if (editingId === id) setEditingId(null);
		setOpenMenuId(null);
		setDeleteConfirmId(null);
	};
	
	const updateRow = (id, field, value) => {
		setData(data.map(row => {
			if (row.id === id) {
				if (field.includes('.')) {
					const [parent, child] = field.split('.');
					return {
						...row,
						[parent]: {
							...row[parent],
							[child]: value
						}
					};
				}
				return { ...row, [field]: value };
			}
			return row;
		}));
	};
	
	const toggleMenu = (id) => {
		setOpenMenuId(openMenuId === id ? null : id);
		setDeleteConfirmId(null);
	};
	
	React.useEffect(() => {
		const handleClickOutside = () => {
			setOpenMenuId(null);
			setDeleteConfirmId(null);
		};
		document.addEventListener('click', handleClickOutside);
		return () => document.removeEventListener('click', handleClickOutside);
	}, []);
	
	const DeleteConfirmDialog = ({ id }) => (
		<div className="absolute right-0 mt-1 w-64 bg-white rounded-lg shadow-sm border border-gray-100 py-2 px-3 z-20">
			<div className="flex items-start space-x-2 text-gray-600 mb-3">
				<AlertCircle size={16} className="text-amber-500 mt-0.5 flex-shrink-0" />
				<p className="text-sm">Are you sure you want to delete this row?</p>
			</div>
			<div className="flex justify-end space-x-2">
				<button
					onClick={(e) => {
						e.stopPropagation();
						setDeleteConfirmId(null);
					}}
					className="px-2 py-1 text-xs text-gray-600 hover:text-gray-800 transition-colors"
				>
					Cancel
				</button>
				<button
					onClick={(e) => {
						e.stopPropagation();
						deleteRow(id);
					}}
					className="px-2 py-1 text-xs text-red-600 hover:text-red-700 transition-colors font-medium"
				>
					Delete
				</button>
			</div>
		</div>
	);
	
	return (
		<div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
			<div className="overflow-x-auto">
				<table className="min-w-full divide-y divide-gray-200">
					<thead className="bg-gray-50/75">
					<tr>
						<th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
						<th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
						<th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Destination</th>
						<th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Label</th>
						<th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
						<th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created By</th>
						<th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
							<div className="flex items-center justify-end gap-4">
								<span>Actions</span>
								<button
									onClick={addNewRow}
									className="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:text-blue-800 transition-colors"
								>
									<Plus size={16} />
								</button>
							</div>
						</th>
					</tr>
					</thead>
					<tbody className="divide-y divide-gray-200">
					{data.map((ref) => (
						<tr key={ref.id} className="hover:bg-gray-50/50 transition-colors">
							<td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-900">
								{ref.id}
							</td>
							<td className="px-6 py-4 whitespace-nowrap">
								{editingId === ref.id ? (
									<input
										type="text"
										value={ref.src_version.name}
										onChange={(e) => updateRow(ref.id, 'src_version.name', e.target.value)}
										className="w-full px-3 py-1.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									/>
								) : (
									<div className="space-y-1">
										<div className="text-sm font-medium text-gray-900">{ref.src_version.name}</div>
										<div className="text-xs text-gray-500">{ref.src_version.asset.slice(0, 8)}</div>
									</div>
								)}
							</td>
							<td className="px-6 py-4 whitespace-nowrap">
								{editingId === ref.id ? (
									<input
										type="text"
										value={ref.dst_version.name}
										onChange={(e) => updateRow(ref.id, 'dst_version.name', e.target.value)}
										className="w-full px-3 py-1.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									/>
								) : (
									<div className="space-y-1">
										<div className="text-sm font-medium text-gray-900">{ref.dst_version.name}</div>
										<div className="text-xs text-gray-500">{ref.dst_version.asset.slice(0, 8)}</div>
									</div>
								)}
							</td>
							<td className="px-6 py-4 whitespace-nowrap">
								{editingId === ref.id ? (
									<input
										type="text"
										value={ref.label}
										onChange={(e) => updateRow(ref.id, 'label', e.target.value)}
										className="w-full px-3 py-1.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									/>
								) : (
									<span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                      {ref.label}
                    </span>
								)}
							</td>
							<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
								{new Date(ref.created_at.replace(/-/g, '/')).toLocaleDateString()}
							</td>
							<td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-500">
								{editingId === ref.id ? (
									<input
										type="text"
										value={ref.created_by}
										onChange={(e) => updateRow(ref.id, 'created_by', e.target.value)}
										className="w-full px-3 py-1.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									/>
								) : (
									ref.created_by
								)}
							</td>
							<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
								<div className="relative">
									{editingId === ref.id ? (
										<div className="flex justify-end space-x-2">
											<button
												onClick={() => setEditingId(null)}
												className="px-3 py-1 text-xs text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors"
											>
												Cancel
											</button>
											<button
												onClick={() => setEditingId(null)}
												className="px-3 py-1 text-xs text-white bg-blue-500 hover:bg-blue-600 rounded-md transition-colors"
											>
												Save
											</button>
										</div>
									) : (
										<>
											<button
												onClick={(e) => {
													e.stopPropagation();
													toggleMenu(ref.id);
												}}
												className="p-1.5 rounded-md hover:bg-gray-50 transition-colors"
											>
												<MoreVertical size={14} className="text-gray-400 hover:text-gray-600" />
											</button>
											
											{openMenuId === ref.id && (
												<div className="absolute right-0 mt-1 w-36 bg-white rounded-lg shadow-sm border border-gray-100 py-1 z-10">
													<button
														onClick={(e) => {
															e.stopPropagation();
															setEditingId(ref.id);
															setOpenMenuId(null);
														}}
														className="w-full px-3 py-1.5 text-left text-sm text-gray-600 hover:bg-gray-50 flex items-center gap-2 transition-colors"
													>
														<Pencil size={13} />
														<span className="text-xs">Edit</span>
													</button>
													<button
														onClick={(e) => {
															e.stopPropagation();
															setDeleteConfirmId(ref.id);
															setOpenMenuId(null);
														}}
														className="w-full px-3 py-1.5 text-left text-sm text-red-500 hover:bg-gray-50 flex items-center gap-2 transition-colors"
													>
														<Trash2 size={13} />
														<span className="text-xs">Delete</span>
													</button>
												</div>
											)}
											
											{deleteConfirmId === ref.id && <DeleteConfirmDialog id={ref.id} />}
										</>
									)}
								</div>
							</td>
						</tr>
					))}
					</tbody>
				</table>
			</div>
		</div>
	);
};

export default RefsTable;
