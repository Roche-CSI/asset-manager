import React, { useEffect, useMemo, useState } from "react";
import Project, { ProjectData, UserRole } from "../../../../servers/asset_server/project";
import UserCard from "pages/projectsPage/v2/cards/UserCard.tsx";
import { ProjectUserForm } from "pages/projectsPage/v2/forms/ProjectUserForm.tsx";
import { StoreNames, useStore } from "../../../../stores";
import { Search, UserPlus } from "lucide-react";
import { useData, UseDataReturnType } from "../../../../hooks/useData";
import Spinner from "../../../../components/spinner/Spinner";
import { Alert } from "../../../../components/errorBoundary";

const UserListView: React.FC<{ project: ProjectData }> = ({ project }) => {
	const [fetchTrigger, setFetchTrigger] = useState(0);
	const [searchTerm, setSearchTerm] = useState<string>("");
	const [roleFilter, setRoleFilter] = useState<"all" | "admin" | "member">("all");
	
	const userStore = useStore(StoreNames.userStore);
	const fetchPromise: Promise<UserRole[]> = useMemo(
		() => Project.getUsersList(userStore.get("user").username, project.name),
		[fetchTrigger]
	);
	const fetchData: UseDataReturnType<UserRole[]> = useData<UserRole[]>(fetchPromise);
	
	const [addUser, setAddUser] = useState<boolean>(false);
	const [editUser, setEditUser] = useState<UserRole | null>(null);
	
	const isAdmin: boolean = userStore.get("projects")?.[project?.id]?.can_admin_project;
	const currentUser = userStore.get("user");
	
	if (!project || !currentUser) {
		return null;
	}
	
	const handleDelete = (userRole) => {
		console.log("User deleted successfully:", userRole);
		setFetchTrigger((prevState) => prevState + 1);
	};
	
	const onAddUser = (data) => {
		console.log("User added successfully:", data);
		setFetchTrigger((prevState) => prevState + 1);
		setAddUser(false);
		setEditUser(null);
	};
	
	const handleEdit = (user: UserRole) => {
		setEditUser(user);
	};
	
	if (fetchData.loading) {
		return <Spinner message={"Loading..."} />;
	}
	
	if (fetchData.error) {
		return (
			<Alert
				title={"Oh Snap! There is an error"}
				variant={"error"}
				message={fetchData.error.toString()}
			/>
		);
	}
	
	if (!fetchData.data) {
		return <span>No data found</span>;
	}
	
	const filteredUsers = fetchData.data.filter(
		(user) =>
			user.email.toLowerCase().includes(searchTerm.toLowerCase()) &&
			(roleFilter === "all" || user.access_level.toLowerCase() === roleFilter)
	);
	
	const roleCount = {
		all: fetchData.data.length,
		admin: fetchData.data.filter((user) => user.access_level.toLowerCase() === "admin").length,
		member: fetchData.data.filter((user) => user.access_level.toLowerCase() === "member").length,
	};
	
	return (
		<div className="bg-base-100 mb-6">
			<div className="flex justify-between mb-4">
				<div className="flex text-neutral-600 space-x-4">
					<div className="flex space-x-4 text-center">
						<div className="text-lg text-neutral mb-6 font-semibold">Project Users</div>
						<span className="text-neutral-400 mt-0.5">#{fetchData.data.length}</span>
					</div>
					<div className="mb-4 relative">
						<input
							type="text"
							placeholder="Search users..."
							value={searchTerm}
							onChange={(e) => setSearchTerm(e.target.value)}
							className="w-full text-xs py-1 pl-10 pr-4 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<Search
							className="absolute -mt-1 left-2 top-1/2 transform -translate-y-1/2 size-4 text-gray-400"/>
					</div>
				</div>
				{isAdmin && !editUser && !addUser && (
					<button
						className={`btn btn-sm btn-secondary rounded-md`}
						onClick={() => setAddUser((prevState) => !prevState)}
					>
						<span>Add User</span>
						<UserPlus className="size-4"/>
					</button>
				)}
			</div>
			
			<div className="flex space-x-4 mb-4">
			{["all", "admin", "member"].map((role) => (
					<button
						key={role}
						onClick={() => setRoleFilter(role as "all" | "admin" | "member")}
						className={`btn btn-xs btn-ghost px-3 py-1 rounded-md text-xs ${
							roleFilter === role
								? "bg-primary text-white"
								: "bg-gray-200 text-gray-700 hover:bg-gray-300"
						}`}
					>
						{role.charAt(0).toUpperCase() + role.slice(1)} ({roleCount[role]})
					</button>
				))}
			</div>
			
			{(addUser || editUser) && (
				<div className="border border-base-300 p-6 max-w-2xl rounded-md mb-6">
					<div className="text-neutral-700 mb-4">
						{editUser ? "Edit Project User" : "Add User to Project"}
					</div>
					<ProjectUserForm
						adminUser={currentUser}
						project={project}
						onSave={onAddUser}
						action={editUser ? "edit" : "create"}
						data={editUser ? editUser : {}}
						onCancel={() => (editUser ? setEditUser(null) : setAddUser(false))}
					/>
				</div>
			)}
			
			{!(addUser || editUser) && (
				<div className="grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 sm:gap-6">
					{filteredUsers.map((userRole: any, idx: number) => (
						<div key={idx} className="outline outline-1 outline-base-300 rounded-md hover:shadow-md">
							<UserCard
								user={userRole}
								onDelete={handleDelete}
								onEdit={handleEdit}
								adminUser={currentUser}
								canEdit={isAdmin}
							/>
						</div>
					))}
				</div>
			)}
		</div>
	);
};

export default UserListView;
