import React, {useState} from "react";
import {BrowserRouter, Route, Routes, useLocation} from "react-router-dom";
import Sidebar from "../sideBar/SideBar";
import {
	AssetPage, ClassListPage, AssetClassPage,
	Dashboard, LoginPage, People, Profile, Teams, Documentation, IssueTracker
} from "../../pages";
import {PrivateRoute} from "./PrivateRoute";
import {AssetClassPageV2} from "../../pages/assetClassPageV2";
import {AssetPageV2} from "../../pages/assetPageV2";
// import {ClassListPageV2} from "../../pages/classListPage/ClassListPageV2";
import {TopNavV2} from "../topNav/TopNavV2";
import ProjectsListPage from "../../pages/projectsPage/v2/ProjectsListPage";
import ProjectInfoPage from "../../pages/projectsPage/v2/ProjectInfoPage";
import ProjectCreate from "../../pages/projectsPage/ProjectCreate";
import ProjectCreatePage from "pages/projectsPage/v2/ProjectCreatePage";

import SearchPage from "pages/searchPage/SearchPage.tsx";
import SearchResultsPage from "pages/searchPage/SearchResultsPage.tsx";
import ProfileV2 from "pages/profilePage/ProfileV2.tsx";

const DefaultLayout = () => {
	const [sidebarOpen, setSidebarOpen] = useState(false)
	
	const location = useLocation();
	const publicRoutes = ['/login', '/', '/login?action=signup'];
	const isPublicRoute = publicRoutes.includes(location.pathname);
	
	return (
		<div className='!bg-white dark:bg-boxdark-2 dark:text-bodydark'>
			{/* <!-- ===== Page Wrapper Start ===== --> */}
			<div className='flex h-screen overflow-hidden'>
				{/* <!-- ===== Sidebar Start ===== --> */}
				{/* <!-- ===== Sidebar End ===== --> */}
				
				{/* <!-- ===== Content Area Start ===== --> */}
				<div className='relative flex flex-1 flex-col overflow-y-auto overflow-x-hidden'>
					{/* <!-- ===== Header Start ===== --> */}
					{!isPublicRoute && (
						<div className="flex sticky top-0 tems-center justify-center">
							{/*<TopNav sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen}/>*/}
							<TopNavV2 sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen}/>
							{/*<TopNavV21/>*/}
						</div>
					)}
					{/* <!-- ===== Header End ===== --> */}
					
					{/* <!-- ===== Main Content Start ===== --> */}
					<div className='flex flex-row '>
						<Sidebar sidebarOpen={sidebarOpen}/>
						
						<main className='w-full'>
							<div>
								<Routes>
									<Route path={"/login"} element={<LoginPage/>}/>
									<Route path="/" element={<Dashboard/>}/>
									<Route path={"/assets/*"}
									       element={<PrivateRoute><ClassListPage/></PrivateRoute>}/>
									<Route path={"/search"} element={<PrivateRoute><SearchPage/></PrivateRoute>}/>
									<Route path={"/search/results/*"} element={<PrivateRoute><SearchResultsPage/></PrivateRoute>}/>
									<Route path={"/people"} element={<PrivateRoute><People/></PrivateRoute>}/>
									<Route path={"/teams"} element={<PrivateRoute><Teams/></PrivateRoute>}/>
									<Route path={"/user/profile"}
									       element={<PrivateRoute><ProfileV2/></PrivateRoute>}/>
									<Route path={"/projects/*"}
									       element={<PrivateRoute><ProjectsListPage/></PrivateRoute>}/>
									<Route path={"/project/:project_id"}
									       element={<PrivateRoute><ProjectInfoPage/></PrivateRoute>}/>
									{/*<Route path={"/projects/create"}*/}
									{/*       element={<PrivateRoute><ProjectCreatePage/></PrivateRoute>}/>*/}
									{/* <Route path={"/settings"} element={<PrivateRoute><Settings/></PrivateRoute>}/> */}
									<Route path={"/asset_class/"}
									       element={<PrivateRoute><AssetClassPageV2/></PrivateRoute>}/>
									<Route path={"/asset/:project_id/:class_name/:seq_id/:view"}
									       element={<PrivateRoute><AssetPageV2/></PrivateRoute>}/>
									<Route path={"/documentation"}
									       element={<PrivateRoute><Documentation/></PrivateRoute>}/>
									<Route path={"/issue"} element={<PrivateRoute><IssueTracker/></PrivateRoute>}/>
									<Route path={"/templates/:template_id"} element={<PrivateRoute></PrivateRoute>}/>
									<Route path={"/not_found"} element={<h1>Resource not found: 404!</h1>}/>
									<Route path="*" element={<h1>There's nothing here: 404!</h1>}/>
								</Routes>
							</div>
						</main>
					</div>
					{/* <!-- ===== Main Content End ===== --> */}
				</div>
				{/* <!-- ===== Content Area End ===== --> */}
			</div>
			{/* <!-- ===== Page Wrapper End ===== --> */}
		</div>
	)
}

export default DefaultLayout;
